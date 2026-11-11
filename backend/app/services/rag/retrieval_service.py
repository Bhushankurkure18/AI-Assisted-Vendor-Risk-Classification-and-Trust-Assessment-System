"""
Evidence Retrieval Service using ChromaDB vector index.
"""
from typing import List, Optional
from backend.app.schemas.rag import EvidenceItem
from backend.app.services.vector_store.chroma_service import ChromaService


class RetrievalService:
    """
    Retrieves evidence items for a given vendor inquiry using semantic search.
    """

    def __init__(self, chroma_service: Optional[ChromaService] = None):
        self.chroma_service = chroma_service or ChromaService()

    def retrieve_evidence(self, vendor_id: int, query: str, top_k: int = 5) -> List[EvidenceItem]:
        raw_items = self.chroma_service.search(vendor_id=vendor_id, query=query, top_k=top_k)
        evidence_items: List[EvidenceItem] = []

        for item in raw_items:
            evidence_items.append(
                EvidenceItem(
                    chunk_id=item["chunk_id"],
                    document_id=item["document_id"],
                    vendor_id=item.get("vendor_id", vendor_id),
                    filename=item.get("filename", ""),
                    page_number=item.get("page_number", 1),
                    section=item.get("section", "General"),
                    chunk_index=item.get("chunk_index", 0),
                    quoted_text=item.get("text", ""),
                    distance=float(item.get("distance", 0.0)),
                )
            )

        return evidence_items

