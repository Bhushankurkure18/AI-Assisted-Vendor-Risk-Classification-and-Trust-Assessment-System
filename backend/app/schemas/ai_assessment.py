"""
Pydantic schemas for Phase 2 Consolidated Multi-Agent AI Assessment.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from backend.app.schemas.rag import EvidenceItem
from backend.app.schemas.agent import AgentFinding
from backend.app.schemas.orchestration import VerificationResult


class AIAssessmentRequest(BaseModel):
    question: str = Field(default="Provide comprehensive risk assessment", description="Assessment focus inquiry")
    alpha: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for Phase 1 quantitative score")
    beta: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for Phase 2 AI multi-agent score")


class AIAssessmentResponse(BaseModel):
    id: int
    vendor_id: int
    created_at: datetime
    phase1_score: float
    phase2_score: float
    final_score: float
    risk_level: str
    financial_score: float
    cybersecurity_score: float
    compliance_score: float
    operational_score: float
    reputation_score: float
    verification_status: str
    overall_confidence: float
    evidence_count: int
    question: Optional[str] = None
    answer: Optional[str] = None
    limitations: Optional[str] = None
    findings: List[AgentFinding] = []
    evidence: List[EvidenceItem] = []

