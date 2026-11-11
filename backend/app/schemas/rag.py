"""
Pydantic schemas for RAG retrieval and question answering.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class EvidenceItem(BaseModel):
    chunk_id: str
    document_id: str
    vendor_id: int
    filename: str
    page_number: int = 1
    section: str = "General"
    chunk_index: int = 0
    quoted_text: str
    distance: float = 0.0


class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Inquiry question regarding vendor risk or profile")
    top_k: int = Field(default=5, ge=1, le=20, description="Maximum number of evidence chunks to retrieve")


class RAGResponse(BaseModel):
    vendor_id: int
    question: str
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = []
    limitations: Optional[str] = None
    status: str = Field(..., description="ANSWERED or INSUFFICIENT_EVIDENCE")

