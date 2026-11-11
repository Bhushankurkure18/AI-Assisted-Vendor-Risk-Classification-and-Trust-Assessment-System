"""
Tests for Phase 2 Milestone 1: Document Ingestion, Extractors, and REST APIs.
"""
import io
import os
import pytest
import docx
import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models.vendor import Vendor
from backend.app.models.document import Document
from backend.app.services.ingestion.document_processor import DocumentProcessor
from backend.app.services.ingestion.pdf_extractor import extract_pdf
from backend.app.services.ingestion.docx_extractor import extract_docx
from backend.app.services.ingestion.txt_extractor import extract_txt
from backend.app.services.ingestion.csv_extractor import extract_csv
from backend.app.services.ingestion.ocr_service import ocr_service

# Isolated SQLite in-memory engine for ingestion tests
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
    # Create test vendor
    v = Vendor(
        vendor_id=101,
        vendor_name="Test Vanguard Logistics",
        revenue=5000000.0,
        debt=1200000.0,
        financial_score=45.0,
        security_score=75.0,
        compliance_score=80.0,
        operational_score=60.0,
        reputation_score=70.0,
    )
    v2 = Vendor(
        vendor_id=102,
        vendor_name="Rival Supply Co",
        revenue=3000000.0,
        debt=500000.0,
        financial_score=60.0,
        security_score=60.0,
        compliance_score=60.0,
        operational_score=60.0,
        reputation_score=60.0,
    )
    db.add(v)
    db.add(v2)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


# 1. Validation & Security Tests

def test_validate_upload_empty_file():
    with pytest.raises(ValueError, match="empty"):
        DocumentProcessor.validate_upload("empty.pdf", b"")


def test_validate_upload_unsupported_ext():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        DocumentProcessor.validate_upload("malicious.exe", b"binarycontent")


def test_validate_upload_oversized(monkeypatch):
    monkeypatch.setattr("backend.app.core.config.settings.MAX_UPLOAD_SIZE_BYTES", 50)
    with pytest.raises(ValueError, match="exceeds maximum"):
        DocumentProcessor.validate_upload("large.txt", b"A" * 100)


def test_sanitize_filename_traversal():
    unsafe = "../../etc/passwd.pdf"
    clean = DocumentProcessor.sanitize_filename(unsafe)
    assert ".." not in clean
    assert "/" not in clean
    assert clean.endswith("passwd.pdf")


def test_compute_sha256():
    h1 = DocumentProcessor.compute_sha256(b"vendor risk data")
    h2 = DocumentProcessor.compute_sha256(b"vendor risk data")
    assert h1 == h2
    assert len(h1) == 64


# 2. Extractor Unit Tests

def test_txt_extractor(tmp_path):
    txt_file = tmp_path / "financial_audit.txt"
    txt_file.write_text("   Quarterly Revenue: $5M.\n\n\nDebt ratio is healthy.   ", encoding="utf-8")
    pages, full_text, method, count = extract_txt(str(txt_file))
    assert count == 1
    assert method == "PLAIN_TEXT"
    assert "Quarterly Revenue: $5M." in full_text
    assert "Debt ratio is healthy." in full_text
    assert "\n\n\n" not in full_text  # Whitespace normalized


def test_csv_extractor(tmp_path):
    csv_file = tmp_path / "supply_orders.csv"
    csv_file.write_text("order_id,lead_time_days,status\nORD-101,14,Delivered\nORD-102,45,Delayed\n")
    pages, full_text, method, count = extract_csv(str(csv_file))
    assert count == 1
    assert method == "PANDAS_CSV"
    assert "Row 1 -> order_id: ORD-101" in full_text
    assert "status: Delayed" in full_text


def test_docx_extractor(tmp_path):
    docx_file = tmp_path / "soc2_report.docx"
    doc = docx.Document()
    doc.add_heading("SOC 2 Type II Compliance Report", level=1)
    doc.add_paragraph("The vendor maintains ISO 27001 and annual SOC 2 audits.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Control"
    table.cell(0, 1).text = "Status"
    table.cell(1, 0).text = "MFA Enforcement"
    table.cell(1, 1).text = "Pass"
    doc.save(str(docx_file))

    pages, full_text, method, count = extract_docx(str(docx_file))
    assert count == 1
    assert method == "PYTHON_DOCX"
    assert "SOC 2 Type II Compliance Report" in full_text
    assert "MFA Enforcement | Pass" in full_text


def test_pdf_extractor_pymupdf(tmp_path):
    pdf_file = tmp_path / "vendor_dossier.pdf"
    doc = fitz.open()
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Financial Statement: Q4 Profit margin reached 18.5%.")
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Security Audit: Penetration tests conducted in November 2026.")
    doc.save(str(pdf_file))
    doc.close()

    pages, full_text, method, count = extract_pdf(str(pdf_file))
    assert count == 2
    assert "PYMUPDF" in method
    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert "Financial Statement" in pages[0].text
    assert pages[1].page_number == 2
    assert "Security Audit" in pages[1].text
    assert "--- Page 1 ---" in full_text
    assert "--- Page 2 ---" in full_text


def test_ocr_service_reporting():
    # Verify OCR service object handles queries safely
    is_avail = ocr_service.is_available()
    assert isinstance(is_avail, bool)


# 3. Ingestion & Duplicate Tests

def test_duplicate_document_detection(tmp_path):
    db = TestingSessionLocal()
    payload = b"Sample contract agreement text for duplicate test"
    d1 = DocumentProcessor.ingest_document(db, 101, "contract_v1.txt", payload, auto_process=True)
    d2 = DocumentProcessor.ingest_document(db, 101, "contract_v2.txt", payload, auto_process=True)
    assert d1.document_id == d2.document_id
    assert d1.content_hash == d2.content_hash
    db.close()


# 4. REST API Endpoints Tests

def test_api_upload_document_success():
    content = b"Official Vendor Compliance Declaration:\n- ISO 27001 Certified\n- Zero GDPR Breaches"
    files = {"file": ("compliance.txt", io.BytesIO(content), "text/plain")}
    response = client.post("/api/v1/documents/upload/101", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["vendor_id"] == 101
    assert data["original_filename"] == "compliance.txt"
    assert data["file_type"] == "txt"
    assert data["processing_status"] == "PROCESSED"
    assert len(data["content_hash"]) == 64


def test_api_upload_document_nonexistent_vendor():
    files = {"file": ("doc.txt", io.BytesIO(b"Hello world"), "text/plain")}
    response = client.post("/api/v1/documents/upload/9999", files=files)
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_api_upload_unsupported_format():
    files = {"file": ("script.sh", io.BytesIO(b"echo 'hi'"), "text/x-sh")}
    response = client.post("/api/v1/documents/upload/101", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


def test_api_list_vendor_documents():
    # Upload two documents
    client.post(
        "/api/v1/documents/upload/101",
        files={"file": ("doc1.txt", io.BytesIO(b"Document 1 text"), "text/plain")}
    )
    client.post(
        "/api/v1/documents/upload/101",
        files={"file": ("doc2.txt", io.BytesIO(b"Document 2 text"), "text/plain")}
    )

    response = client.get("/api/v1/documents/vendor/101")
    assert response.status_code == 200
    data = response.json()
    assert data["vendor_id"] == 101
    assert data["total"] >= 2
    assert len(data["documents"]) >= 2


def test_api_get_document_detail_correct_vendor():
    upload_res = client.post(
        "/api/v1/documents/upload/101",
        files={"file": ("audit_summary.txt", io.BytesIO(b"Vendor Audit Summary Findings"), "text/plain")}
    )
    doc_id = upload_res.json()["document_id"]

    # Correct vendor 101 accessing its own document
    detail_res = client.get(f"/api/v1/documents/101/{doc_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["document_id"] == doc_id
    assert detail["vendor_id"] == 101
    assert "Vendor Audit Summary Findings" in detail["extracted_text"]
    assert detail["processing_status"] == "PROCESSED"


def test_api_get_document_detail_different_vendor():
    upload_res = client.post(
        "/api/v1/documents/upload/101",
        files={"file": ("confidential.txt", io.BytesIO(b"Confidential Vendor 101 Data"), "text/plain")}
    )
    doc_id = upload_res.json()["document_id"]

    # Different vendor 102 attempting to access vendor 101's document
    detail_res = client.get(f"/api/v1/documents/102/{doc_id}")
    assert detail_res.status_code == 404
    assert f"Document {doc_id} not found for vendor 102" in detail_res.json()["detail"]


def test_api_get_document_detail_nonexistent_document():
    # Valid vendor 101 querying a nonexistent document ID
    detail_res = client.get("/api/v1/documents/101/doc_nonexistent999")
    assert detail_res.status_code == 404
    assert "Document doc_nonexistent999 not found for vendor 101" in detail_res.json()["detail"]


def test_api_get_document_detail_nonexistent_vendor():
    # Nonexistent vendor 9999 querying a document
    detail_res = client.get("/api/v1/documents/9999/doc_anyid123")
    assert detail_res.status_code == 404
    assert "Vendor 9999 not found" in detail_res.json()["detail"]


def test_api_reprocess_document():
    upload_res = client.post(
        "/api/v1/documents/upload/101",
        files={"file": ("reprocess_test.txt", io.BytesIO(b"Text before reprocess"), "text/plain")}
    )
    doc_id = upload_res.json()["document_id"]

    # Test vendor-scoped reprocess endpoint
    process_res = client.post(f"/api/v1/documents/101/{doc_id}/process")
    assert process_res.status_code == 200
    pdata = process_res.json()
    assert pdata["document_id"] == doc_id
    assert pdata["processing_status"] == "PROCESSED"
    assert pdata["total_characters"] > 0
    assert len(pdata["pages"]) == 1

