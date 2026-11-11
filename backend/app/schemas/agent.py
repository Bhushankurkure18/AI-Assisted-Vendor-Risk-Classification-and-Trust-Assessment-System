"""
Pydantic schemas for AI Agent Analysis.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.app.schemas.rag import EvidenceItem


class AgentFinding(BaseModel):
    agent_name: str
    dimension: str
    score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    evidence_references: List[EvidenceItem] = []
    missing_information: List[str] = []
    reasoning_summary: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: str = Field(..., description="ANALYZED or INSUFFICIENT_EVIDENCE")

