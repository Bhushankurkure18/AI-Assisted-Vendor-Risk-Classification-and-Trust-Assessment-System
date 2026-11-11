"""
RAG Service for Grounded Question Answering and Evidence Verification.
"""
from typing import List, Optional
from backend.app.schemas.rag import EvidenceItem, RAGResponse
from backend.app.services.rag.retrieval_service import RetrievalService


class RAGService:
    """
    Evidence-grounded RAG query service. Strictly relies on retrieved document chunks.
    Does not hallucinate answers when evidence is missing.
    """

    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.retrieval_service = retrieval_service or RetrievalService()

    def query(self, vendor_id: int, question: str, top_k: int = 5) -> RAGResponse:
        evidence = self.retrieval_service.retrieve_evidence(vendor_id=vendor_id, query=question, top_k=top_k)

        if not evidence:
            return RAGResponse(
                vendor_id=vendor_id,
                question=question,
                answer="No relevant evidence found in uploaded vendor documentation. Assessment cannot be substantiated without source documents.",
                confidence=0.0,
                evidence=[],
                limitations="Insufficient evidence: No document chunks matched the query in the vector store.",
                status="INSUFFICIENT_EVIDENCE",
            )

        # Formulate grounded answer from extracted evidence
        snippets = []
        for i, ev in enumerate(evidence, 1):
            snippets.append(
                f"[Source: {ev.filename}, Page {ev.page_number}, Section: {ev.section}]\n\"{ev.quoted_text.strip()}\""
            )

        answer_body = "\n\n".join(snippets)
        answer = f"Based on retrieved vendor documentation, the following evidence was identified:\n\n{answer_body}"

        # Confidence is derived from distance / similarity (cosine distance: closer to 0 is higher similarity)
        # Avg distance mapped to confidence: 1.0 - min(1.0, avg_dist)
        avg_dist = sum(e.distance for e in evidence) / len(evidence)
        confidence = round(max(0.1, min(1.0, 1.0 - (avg_dist / 2.0))), 2)

        return RAGResponse(
            vendor_id=vendor_id,
            question=question,
            answer=answer,
            confidence=confidence,
            evidence=evidence,
            limitations="Deterministic evidence-based retrieval. Answers are directly extracted from indexed source documents.",
            status="ANSWERED",
        )

