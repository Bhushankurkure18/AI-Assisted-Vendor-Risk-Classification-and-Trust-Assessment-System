"""
Unit and API integration tests for Phase 2 Milestone 2: Text Cleaning, Deduplication, and Chunking.
"""
import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models.vendor import Vendor
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.services.chunking.text_cleaner import TextCleaner
from backend.app.services.chunking.deduplication import DeduplicationHandler
from backend.app.services.chunking.chunking_service import ChunkingService

# Test database setup
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test vendors
    v1 = Vendor(
        vendor_id=201,
        vendor_name="Acme Aerospace",
        revenue=10000000.0,
        debt=2500000.0,
        financial_score=55.0,
        security_score=80.0,
        compliance_score=85.0,
        operational_score=70.0,
        reputation_score=75.0,
    )
    v2 = Vendor(
        vendor_id=202,
        vendor_name="Bravo Logistics",
        revenue=4000000.0,
        debt=800000.0,
        financial_score=40.0,
        security_score=65.0,
        compliance_score=70.0,
        operational_score=50.0,
        reputation_score=60.0,
    )
    db.add(v1)
    db.add(v2)
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


# 1. Text Cleaner Tests

def test_text_cleaner_boilerplate_removal():
    dirty_text = (
        "CONFIDENTIAL\n"
        "Page 1 of 12\n"
        "Financial Statement Q3 2026.\n"
        "Revenue grew by 14.2% to $12.5M. Operating expenses remained stable.\n"
        "Strictly Private and Confidential\n"
        "Page 2\n"
        "Debt-to-equity ratio improved to 0.45.\n"
    )
    cleaned = TextCleaner.clean_text(dirty_text)
    assert "CONFIDENTIAL" not in cleaned
    assert "Page 1 of 12" not in cleaned
    assert "Financial Statement Q3 2026." in cleaned
    assert "Revenue grew by 14.2% to $12.5M." in cleaned
    assert "Debt-to-equity ratio improved to 0.45." in cleaned


def test_text_cleaner_section_detection():
    assert TextCleaner.detect_heading("# 1. Financial Overview") == "1. Financial Overview"
    assert TextCleaner.detect_heading("2.3 Cybersecurity Controls") == "2.3 Cybersecurity Controls"
    assert TextCleaner.detect_heading("[Compliance Audit]") == "Compliance Audit"
    assert TextCleaner.detect_heading("Regular paragraph text that is not a heading.") is None


# 2. Deduplication Tests

def test_deduplication_handler():
    t1 = "Vendor incurred a data breach in June 2025."
    t2 = "Vendor incurred a data breach in June 2025."
    t3 = "Vendor achieved ISO 27001 certification."

    h1 = DeduplicationHandler.compute_chunk_hash(t1)
    h2 = DeduplicationHandler.compute_chunk_hash(t2)
    h3 = DeduplicationHandler.compute_chunk_hash(t3)

    assert h1 == h2
    assert h1 != h3

    raw_chunks = [
        {"content_hash": h1, "text": t1},
        {"content_hash": h2, "text": t2},
        {"content_hash": h3, "text": t3},
    ]
    unique = DeduplicationHandler.filter_duplicate_chunks(raw_chunks)
    assert len(unique) == 2


# 3. Chunking Service Tests

def test_chunking_service_token_and_sentence_preservation():
    # Long text with distinct sentences
    sentences = [
        f"Sentence {i}: Vendor reported operational stability across facility {i}."
        for i in range(1, 40)
    ]
    text = " ".join(sentences)

    chunks = ChunkingService.chunk_document_text(
        document_id="doc_test_100",
        vendor_id=201,
        filename="operations.txt",
        raw_text=text,
        chunk_size_tokens=60,  # Small token threshold to force multiple chunks
        chunk_overlap_tokens=15,
    )

    assert len(chunks) > 1
    for c in chunks:
        assert c["document_id"] == "doc_test_100"
        assert c["vendor_id"] == 201
        assert c["token_count"] > 0
        assert len(c["content_hash"]) == 64
        # Sentence boundary: chunk must not start with fragment
        assert c["text"].startswith("Sentence ")


def test_chunking_service_multi_page_preservation():
    pages_data = [
        {"page_number": 1, "text": "Page 1: Financial disclosures. Current assets total $45M."},
        {"page_number": 2, "text": "Page 2: Cybersecurity assessment. SOC 2 Type II audit verified."},
    ]
    chunks = ChunkingService.chunk_document_text(
        document_id="doc_multi_page",
        vendor_id=201,
        filename="dossier.pdf",
        pages_data=pages_data,
        chunk_size_tokens=100,
    )

    page_nums = [c["page_number"] for c in chunks]
    assert 1 in page_nums
    assert 2 in page_nums


def test_chunking_service_persist_and_idempotency():
    db = TestingSessionLocal()
    # Create document
    doc = Document(
        document_id="doc_persist_test",
        vendor_id=201,
        original_filename="audit.txt",
        stored_filepath="data/uploads/201/doc_persist_test_audit.txt",
        file_type="txt",
        file_size=500,
        content_hash="dummyhash123",
        processing_status="PROCESSED",
        extracted_text="1.0 Financial Audit\n\nRevenue is $10M. Debt is $2M. Solvency is robust.",
    )
    db.add(doc)
    db.commit()

    # First chunking run
    chunks_1 = ChunkingService.chunk_and_persist(db, "doc_persist_test")
    assert len(chunks_1) >= 1
    assert chunks_1[0].section == "1.0 Financial Audit"

    # Second chunking run (idempotency check)
    chunks_2 = ChunkingService.chunk_and_persist(db, "doc_persist_test")
    total_in_db = db.query(DocumentChunk).filter(DocumentChunk.document_id == "doc_persist_test").count()
    assert total_in_db == len(chunks_2)
    db.close()


# 4. REST API Endpoint Tests

def test_api_chunk_document_endpoint():
    # 1. Upload document
    upload_res = client.post(
        "/api/v1/documents/upload/201",
        files={"file": ("sec_filing.txt", io.BytesIO(b"Item 1. Business Overview.\nVendor provides cloud logistics."), "text/plain")}
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["document_id"]

    # 2. Call chunk endpoint
    chunk_res = client.post(f"/api/v1/documents/201/{doc_id}/chunk")
    assert chunk_res.status_code == 200
    cdata = chunk_res.json()
    assert cdata["document_id"] == doc_id
    assert cdata["vendor_id"] == 201
    assert cdata["total_chunks"] >= 1
    assert len(cdata["chunks"]) >= 1


def test_api_list_document_chunks_endpoint():
    upload_res = client.post(
        "/api/v1/documents/upload/201",
        files={"file": ("report.txt", io.BytesIO(b"Page 1: Full vendor report text."), "text/plain")}
    )
    doc_id = upload_res.json()["document_id"]
    client.post(f"/api/v1/documents/201/{doc_id}/chunk")

    # List chunks for document
    res = client.get(f"/api/v1/documents/201/{doc_id}/chunks")
    assert res.status_code == 200
    data = res.json()
    assert data["document_id"] == doc_id
    assert data["total_chunks"] >= 1


def test_api_list_vendor_chunks_endpoint():
    upload_res = client.post(
        "/api/v1/documents/upload/201",
        files={"file": ("doc_a.txt", io.BytesIO(b"Data for vendor chunk aggregation."), "text/plain")}
    )
    doc_id = upload_res.json()["document_id"]
    client.post(f"/api/v1/documents/201/{doc_id}/chunk")

    # List all chunks for vendor 201
    res = client.get("/api/v1/documents/vendor/201/chunks")
    assert res.status_code == 200
    data = res.json()
    assert data["vendor_id"] == 201
    assert data["total_chunks"] >= 1

