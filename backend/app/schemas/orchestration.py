"""
Schemas for LangGraph Orchestration and Verification.
"""
from typing import List, Optional, Dict, Any, TypedDict
from pydantic import BaseModel, Field
from backend.app.schemas.rag import EvidenceItem
from backend.app.schemas.agent import AgentFinding


class VerificationResult(BaseModel):
    status: str = Field(..., description="VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, or INSUFFICIENT_EVIDENCE")
    verified_count: int
    total_findings: int
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    details: List[str] = []


class WorkflowState(TypedDict, total=False):
    vendor_id: int
    question: str
    evidence_chunks: List[EvidenceItem]
    financial_finding: Optional[AgentFinding]
    cybersecurity_finding: Optional[AgentFinding]
    compliance_finding: Optional[AgentFinding]
    operational_finding: Optional[AgentFinding]
    reputation_finding: Optional[AgentFinding]
    verification_result: Optional[VerificationResult]
    errors: List[str]

