"""
Tests for ChromaService Vector Store.
"""
import pytest
import chromadb
from backend.app.services.vector_store.chroma_service import ChromaService


@pytest.fixture
def temp_chroma_service(tmp_path):
    """Fixture providing isolated ChromaService using temporary directory."""
    persist_dir = str(tmp_path / "chroma_test_db")
    service = ChromaService(persist_directory=persist_dir)
    return service


def test_add_and_search_returns_results(temp_chroma_service):
    chunks = [
        {
            "chunk_id": "chk_001",
            "document_id": "doc_001",
            "vendor_id": 1,
            "filename": "security_audit.pdf",
            "page_number": 1,
            "section": "Cybersecurity",
            "chunk_index": 0,
            "text": "The vendor maintains ISO 27001 certification and encrypts data at rest.",
        },
        {
            "chunk_id": "chk_002",
            "document_id": "doc_001",
            "vendor_id": 1,
            "filename": "security_audit.pdf",
            "page_number": 2,
            "section": "Compliance",
            "chunk_index": 1,
            "text": "Regular quarterly third-party penetration testing is performed.",
        }
    ]
    upserted = temp_chroma_service.add_chunks(vendor_id=1, chunks=chunks)
    assert upserted == 2

    results = temp_chroma_service.search(vendor_id=1, query="penetration testing audit", top_k=2)
    assert len(results) > 0
    assert "penetration testing" in results[0]["text"]
    assert results[0]["chunk_id"] == "chk_002"
    assert results[0]["vendor_id"] == 1


def test_search_vendor_isolation(temp_chroma_service):
    # Vendor 1 chunks
    chunks_v1 = [{
        "chunk_id": "v1_chk_1",
        "document_id": "v1_doc_1",
        "vendor_id": 101,
        "filename": "v1_finances.txt",
        "page_number": 1,
        "text": "Vendor 101 annual revenue was 50 million dollars with zero debt.",
    }]
    # Vendor 2 chunks
    chunks_v2 = [{
        "chunk_id": "v2_chk_1",
        "document_id": "v2_doc_1",
        "vendor_id": 102,
        "filename": "v2_finances.txt",
        "page_number": 1,
        "text": "Vendor 102 filed for bankruptcy protection under Chapter 11.",
    }]

    temp_chroma_service.add_chunks(vendor_id=101, chunks=chunks_v1)
    temp_chroma_service.add_chunks(vendor_id=102, chunks=chunks_v2)

    # Search for bankruptcy under vendor 101 -> must NOT return vendor 102 chunks
    results_v1 = temp_chroma_service.search(vendor_id=101, query="bankruptcy debt revenue")
    assert len(results_v1) == 1
    assert results_v1[0]["vendor_id"] == 101
    assert "Vendor 101" in results_v1[0]["text"]

    # Search under vendor 102 -> returns only vendor 102
    results_v2 = temp_chroma_service.search(vendor_id=102, query="bankruptcy")
    assert len(results_v2) == 1
    assert results_v2[0]["vendor_id"] == 102
    assert "Vendor 102" in results_v2[0]["text"]


def test_delete_document_removes_embeddings(temp_chroma_service):
    chunks = [
        {
            "chunk_id": "chk_del_1",
            "document_id": "doc_to_delete",
            "vendor_id": 200,
            "filename": "file.pdf",
            "text": "Confidential financial statements.",
        },
        {
            "chunk_id": "chk_keep_1",
            "document_id": "doc_to_keep",
            "vendor_id": 200,
            "filename": "keep.pdf",
            "text": "Operational continuity plan and disaster recovery.",
        }
    ]
    temp_chroma_service.add_chunks(vendor_id=200, chunks=chunks)
    assert temp_chroma_service.get_stats(vendor_id=200)["total_chunks"] == 2

    deleted_count = temp_chroma_service.delete_document("doc_to_delete")
    assert deleted_count == 1
    assert temp_chroma_service.get_stats(vendor_id=200)["total_chunks"] == 1

    results = temp_chroma_service.search(vendor_id=200, query="confidential financial statements")
    # Only keep doc should be found or none match closely
    for r in results:
        assert r["document_id"] != "doc_to_delete"


def test_get_stats_returns_correct_count(temp_chroma_service):
    assert temp_chroma_service.get_stats(vendor_id=300)["total_chunks"] == 0

    chunks = [
        {"chunk_id": f"chk_{i}", "document_id": "doc_stat", "vendor_id": 300, "text": f"Policy rule number {i}"}
        for i in range(5)
    ]
    temp_chroma_service.add_chunks(vendor_id=300, chunks=chunks)
    stats = temp_chroma_service.get_stats(vendor_id=300)
    assert stats["total_chunks"] == 5
    assert stats["vendor_id"] == 300


def test_search_empty_collection_returns_empty_list(temp_chroma_service):
    results = temp_chroma_service.search(vendor_id=999, query="anything")
    assert results == []

