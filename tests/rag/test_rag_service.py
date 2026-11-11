"""
Tests for RAG Retrieval and Question Answering Service.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models.vendor import Vendor
from backend.app.services.vector_store.chroma_service import ChromaService
from backend.app.services.rag.retrieval_service import RetrievalService
from backend.app.services.rag.rag_service import RAGService


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rag_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def isolated_rag_service(tmp_path):
    chroma_dir = str(tmp_path / "rag_chroma_db")
    chroma_svc = ChromaService(persist_directory=chroma_dir)
    retrieval_svc = RetrievalService(chroma_service=chroma_svc)
    rag_svc = RAGService(retrieval_service=retrieval_svc)
    return chroma_svc, rag_svc


def test_rag_query_with_evidence_returns_answered(isolated_rag_service):
    chroma_svc, rag_svc = isolated_rag_service
    chroma_svc.add_chunks(
        vendor_id=50,
        chunks=[{
            "chunk_id": "c1",
            "document_id": "d1",
            "vendor_id": 50,
            "filename": "iso_certificate.pdf",
            "page_number": 3,
            "section": "Certifications",
            "text": "Acme Corp holds an active ISO/IEC 27001:2022 cybersecurity certification verified in 2026."
        }]
    )

    response = rag_svc.query(vendor_id=50, question="What certifications does Acme hold?", top_k=3)
    assert response.status == "ANSWERED"
    assert response.confidence > 0.0
    assert len(response.evidence) == 1
    assert "ISO/IEC 27001" in response.answer
    assert response.evidence[0].filename == "iso_certificate.pdf"
    assert response.evidence[0].page_number == 3


def test_rag_query_no_evidence_returns_insufficient(isolated_rag_service):
    _, rag_svc = isolated_rag_service
    response = rag_svc.query(vendor_id=999, question="What is their financial debt?", top_k=5)
    assert response.status == "INSUFFICIENT_EVIDENCE"
    assert response.confidence == 0.0
    assert len(response.evidence) == 0
    assert "No relevant evidence" in response.answer


def test_evidence_items_have_required_fields(isolated_rag_service):
    chroma_svc, rag_svc = isolated_rag_service
    chroma_svc.add_chunks(
        vendor_id=77,
        chunks=[{
            "chunk_id": "chk_77",
            "document_id": "doc_77",
            "vendor_id": 77,
            "filename": "sla.docx",
            "page_number": 1,
            "section": "SLA Terms",
            "text": "Vendor agrees to a 99.9% uptime SLA with 2-hour disaster recovery."
        }]
    )

    response = rag_svc.query(vendor_id=77, question="What is the SLA?", top_k=1)
    ev = response.evidence[0]
    assert ev.chunk_id == "chk_77"
    assert ev.document_id == "doc_77"
    assert ev.vendor_id == 77
    assert ev.filename == "sla.docx"
    assert ev.page_number == 1
    assert ev.section == "SLA Terms"
    assert "99.9% uptime" in ev.quoted_text


def test_rag_api_endpoint():
    db = TestingSessionLocal()
    v = Vendor(
        vendor_id=888,
        vendor_name="Test Vendor RAG",
        financial_score=30.0,
        security_score=25.0,
        compliance_score=20.0,
        operational_score=20.0,
        reputation_score=15.0,
    )
    db.merge(v)
    db.commit()
    db.close()

    res = client.post(
        "/api/v1/rag/vendors/888/ask",
        json={"question": "What is the cybersecurity policy?", "top_k": 3}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["vendor_id"] == 888
    assert "status" in data
    assert "confidence" in data
    assert "evidence" in data

    # 404 for non-existent vendor
    res_404 = client.post(
        "/api/v1/rag/vendors/999999/ask",
        json={"question": "Test", "top_k": 2}
    )
    assert res_404.status_code == 404
