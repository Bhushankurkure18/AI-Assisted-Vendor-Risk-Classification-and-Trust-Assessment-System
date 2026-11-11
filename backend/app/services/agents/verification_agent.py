"""
Verification Agent for Cross-Checking Agent Conclusions against Stored Evidence.
"""
from typing import List
from backend.app.schemas.rag import EvidenceItem
from backend.app.schemas.agent import AgentFinding
from backend.app.schemas.orchestration import VerificationResult


class VerificationAgent:
    """
    Audits and validates risk agent conclusions against authentic retrieved evidence items.
    Prevents hallucination and phantom citations.
    """

    @classmethod
    def verify(cls, findings: List[AgentFinding], all_evidence: List[EvidenceItem]) -> VerificationResult:
        if not findings:
            return VerificationResult(
                status="INSUFFICIENT_EVIDENCE",
                verified_count=0,
                total_findings=0,
                overall_confidence=0.0,
                details=["No agent findings submitted for verification."],
            )

        evidence_chunk_ids = {ev.chunk_id for ev in all_evidence}
        verified_count = 0
        details: List[str] = []
        confidences: List[float] = []

        for f in findings:
            if f.status == "INSUFFICIENT_EVIDENCE":
                details.append(f"{f.agent_name} reported insufficient documentation for {f.dimension}.")
                continue

            ref_ids = [ref.chunk_id for ref in f.evidence_references]
            if not ref_ids:
                details.append(f"{f.agent_name}: No evidence citations provided.")
                continue

            # Verify citations against retrieved chunk IDs
            matched = [cid for cid in ref_ids if cid in evidence_chunk_ids]
            if len(matched) == len(ref_ids):
                verified_count += 1
                confidences.append(f.confidence)
                details.append(f"{f.agent_name}: All {len(ref_ids)} citations verified against retrieved evidence.")
            elif len(matched) > 0:
                verified_count += 1
                confidences.append(f.confidence * 0.7)
                details.append(f"{f.agent_name}: Partially verified ({len(matched)}/{len(ref_ids)} citations matched).")
            else:
                details.append(f"{f.agent_name}: UNVERIFIED. Referenced chunks not present in retrieved evidence.")

        total_findings = len(findings)
        if total_findings == 0:
            status = "INSUFFICIENT_EVIDENCE"
            overall_confidence = 0.0
        elif verified_count == total_findings:
            status = "VERIFIED"
            overall_confidence = round(sum(confidences) / max(1, len(confidences)), 2)
        elif verified_count > 0:
            status = "PARTIALLY_VERIFIED"
            overall_confidence = round(sum(confidences) / max(1, len(confidences)), 2)
        else:
            status = "UNVERIFIED"
            overall_confidence = 0.0

        return VerificationResult(
            status=status,
            verified_count=verified_count,
            total_findings=total_findings,
            overall_confidence=overall_confidence,
            details=details,
        )

