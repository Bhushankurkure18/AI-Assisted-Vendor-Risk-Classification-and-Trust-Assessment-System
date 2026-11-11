"""
AI Assessment REST Endpoints for Multi-Agent Vendor Risk Intelligence.
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.models.vendor import Vendor
from backend.app.models.assessment import Assessment
from backend.app.models.ai_assessment import AIAssessment
from backend.app.schemas.ai_assessment import AIAssessmentRequest, AIAssessmentResponse
from backend.app.services.orchestration.workflow import RiskWorkflow
from backend.app.services.aggregation.risk_aggregation import RiskAggregationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/assessments/ai",
    tags=["Phase 2 - Multi-Agent AI Assessment"],
)

workflow = RiskWorkflow()


@router.post(
    "/vendors/{vendor_id}/run",
    response_model=AIAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run full Multi-Agent LangGraph RAG Risk Assessment",
)
def run_ai_assessment(
    vendor_id: int,
    request: AIAssessmentRequest,
    db: Session = Depends(get_db),
):
    """
    Executes end-to-end multi-agent evaluation:
    1. Fetches vendor and baseline Phase 1 quantitative assessment
    2. Runs LangGraph state graph across 5 risk dimensions
    3. Verifies agent conclusions against retrieved evidence chunks
    4. Aggregates Phase 1 + Phase 2 scores into final risk classification
    5. Persists consolidated record in database
    """
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} does not exist.",
        )

    # 1. Obtain Phase 1 score (latest from assessments or compute from vendor baseline)
    latest_phase1 = (
        db.query(Assessment)
        .filter(Assessment.vendor_id == vendor_id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if latest_phase1:
        phase1_score = float(latest_phase1.overall_risk_score)
    else:
        # Fallback to vendor table attributes
        p1_weighted = (
            (vendor.financial_score * 0.25)
            + (vendor.security_score * 0.25)
            + (vendor.compliance_score * 0.20)
            + (vendor.operational_score * 0.20)
            + (vendor.reputation_score * 0.10)
        )
        phase1_score = float(p1_weighted)

    # 2. Run LangGraph workflow
    state = workflow.run(vendor_id=vendor_id, question=request.question)

    findings = []
    for key in [
        "financial_finding",
        "cybersecurity_finding",
        "compliance_finding",
        "operational_finding",
        "reputation_finding",
    ]:
        f = state.get(key)
        if f is not None:
            findings.append(f)

    # 3. Aggregate scores
    agg = RiskAggregationService.aggregate(
        phase1_score=phase1_score,
        findings=findings,
        alpha=request.alpha,
        beta=request.beta,
    )

    verification = state.get("verification_result")
    ver_status = verification.status if verification else "UNVERIFIED"
    overall_conf = verification.overall_confidence if verification else 0.5
    evidence_chunks = state.get("evidence_chunks", [])

    # Compose answer summary
    answer_parts = [
        f"Consolidated AI assessment executed for vendor {vendor.vendor_name}.",
        f"Overall Risk Classification: {agg['risk_level']} (Final Score: {agg['final_score']:.1f}/100).",
        f"Phase 1 Quantitative Score: {agg['phase1_score']:.1f}, Phase 2 AI Evidence Score: {agg['phase2_score']:.1f}.",
        f"Verification Status: {ver_status} based on {len(evidence_chunks)} retrieved evidence passages.",
    ]
    answer_text = "\n".join(answer_parts)

    # Serialize JSON state
    json_blob = json.dumps({
        "vendor_id": vendor_id,
        "aggregation": agg,
        "verification": verification.model_dump() if verification else None,
        "findings": [f.model_dump() for f in findings],
    }, default=str)

    # 4. Persist to DB
    record = AIAssessment(
        vendor_id=vendor_id,
        phase1_score=agg["phase1_score"],
        phase2_score=agg["phase2_score"],
        final_score=agg["final_score"],
        risk_level=agg["risk_level"],
        financial_score=agg["financial_score"],
        cybersecurity_score=agg["cybersecurity_score"],
        compliance_score=agg["compliance_score"],
        operational_score=agg["operational_score"],
        reputation_score=agg["reputation_score"],
        verification_status=ver_status,
        overall_confidence=overall_conf,
        evidence_count=len(evidence_chunks),
        question=request.question,
        answer=answer_text,
        limitations="Multi-agent evidence evaluation. All findings audited against stored document passages.",
        assessment_json=json_blob,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return AIAssessmentResponse(
        id=record.id,
        vendor_id=record.vendor_id,
        created_at=record.created_at,
        phase1_score=record.phase1_score,
        phase2_score=record.phase2_score,
        final_score=record.final_score,
        risk_level=record.risk_level,
        financial_score=record.financial_score,
        cybersecurity_score=record.cybersecurity_score,
        compliance_score=record.compliance_score,
        operational_score=record.operational_score,
        reputation_score=record.reputation_score,
        verification_status=record.verification_status,
        overall_confidence=record.overall_confidence,
        evidence_count=record.evidence_count,
        question=record.question,
        answer=record.answer,
        limitations=record.limitations,
        findings=findings,
        evidence=evidence_chunks,
    )


@router.get(
    "/vendors/{vendor_id}/latest",
    response_model=AIAssessmentResponse,
    summary="Get latest AI assessment for a vendor",
)
def get_latest_ai_assessment(
    vendor_id: int,
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} does not exist.",
        )

    record = (
        db.query(AIAssessment)
        .filter(AIAssessment.vendor_id == vendor_id)
        .order_by(AIAssessment.created_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No AI assessments found for vendor {vendor_id}. Run an assessment first.",
        )

    # Parse findings from JSON blob
    findings = []
    if record.assessment_json:
        try:
            data = json.loads(record.assessment_json)
            raw_findings = data.get("findings", [])
            for rf in raw_findings:
                from backend.app.schemas.agent import AgentFinding
                findings.append(AgentFinding(**rf))
        except Exception:
            pass

    return AIAssessmentResponse(
        id=record.id,
        vendor_id=record.vendor_id,
        created_at=record.created_at,
        phase1_score=record.phase1_score,
        phase2_score=record.phase2_score,
        final_score=record.final_score,
        risk_level=record.risk_level,
        financial_score=record.financial_score,
        cybersecurity_score=record.cybersecurity_score,
        compliance_score=record.compliance_score,
        operational_score=record.operational_score,
        reputation_score=record.reputation_score,
        verification_status=record.verification_status,
        overall_confidence=record.overall_confidence,
        evidence_count=record.evidence_count,
        question=record.question,
        answer=record.answer,
        limitations=record.limitations,
        findings=findings,
        evidence=[],
    )


@router.get(
    "/vendors/{vendor_id}/history",
    response_model=List[AIAssessmentResponse],
    summary="Get history of AI assessments for a vendor",
)
def get_ai_assessment_history(
    vendor_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} does not exist.",
        )

    records = (
        db.query(AIAssessment)
        .filter(AIAssessment.vendor_id == vendor_id)
        .order_by(AIAssessment.created_at.desc())
        .limit(limit)
        .all()
    )

    items = []
    for r in records:
        items.append(
            AIAssessmentResponse(
                id=r.id,
                vendor_id=r.vendor_id,
                created_at=r.created_at,
                phase1_score=r.phase1_score,
                phase2_score=r.phase2_score,
                final_score=r.final_score,
                risk_level=r.risk_level,
                financial_score=r.financial_score,
                cybersecurity_score=r.cybersecurity_score,
                compliance_score=r.compliance_score,
                operational_score=r.operational_score,
                reputation_score=r.reputation_score,
                verification_status=r.verification_status,
                overall_confidence=r.overall_confidence,
                evidence_count=r.evidence_count,
                question=r.question,
                answer=r.answer,
                limitations=r.limitations,
                findings=[],
                evidence=[],
            )
        )
    return items

