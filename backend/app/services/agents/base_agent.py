"""
Base Risk Agent interface and keyword evaluation logic.
"""
from typing import List, Dict, Any, Optional
from backend.app.schemas.rag import EvidenceItem
from backend.app.schemas.agent import AgentFinding


class BaseRiskAgent:
    """
    Abstract base class for deterministic evidence-based risk assessment agents.
    Grounds findings directly on retrieved evidence chunks and evaluates presence of risk indicators.
    """

    agent_name: str = "BaseAgent"
    dimension: str = "General"
    keywords: List[str] = []

    @classmethod
    def map_score_to_level(cls, score: float) -> str:
        """
        Maps numeric score (0-100) to risk level following Phase 1 thresholds:
        0 - 39: LOW
        40 - 69: MEDIUM
        70 - 100: HIGH
        """
        if score <= 39.0:
            return "LOW"
        elif score <= 69.0:
            return "MEDIUM"
        else:
            return "HIGH"

    @classmethod
    def analyze(cls, vendor_id: int, evidence_chunks: List[EvidenceItem]) -> AgentFinding:
        if not evidence_chunks:
            return AgentFinding(
                agent_name=cls.agent_name,
                dimension=cls.dimension,
                score=50.0,
                risk_level="MEDIUM",
                evidence_references=[],
                missing_information=cls.keywords[:5],
                reasoning_summary=f"No evidence retrieved from documentation for {cls.dimension} dimension. Baseline assumption applied.",
                confidence=0.0,
                status="INSUFFICIENT_EVIDENCE",
            )

        # Scan text for keywords
        found_keywords = set()
        total_mentions = 0
        relevant_chunks: List[EvidenceItem] = []

        for chk in evidence_chunks:
            txt_lower = chk.quoted_text.lower()
            chunk_has_kw = False
            for kw in cls.keywords:
                if kw in txt_lower:
                    found_keywords.add(kw)
                    total_mentions += 1
                    chunk_has_kw = True
            if chunk_has_kw:
                relevant_chunks.append(chk)

        missing_keywords = [kw for kw in cls.keywords if kw not in found_keywords]

        # Calculate evidence-based risk score:
        # Base confidence from presence of evidence
        # More mentions/documentation of controls or risk areas allows assessment
        # Inverse risk heuristic: well-documented evidence correlates with lower/medium manageable risk (unless breach/loss keywords dominate)
        negative_indicators = {"breach", "hack", "loss", "debt", "bankruptcy", "violation", "penalty", "disruption", "downtime", "complaint"}
        negative_hits = sum(1 for kw in found_keywords if kw in negative_indicators)

        if negative_hits > 0:
            score = min(95.0, 45.0 + (negative_hits * 15.0))
        elif len(found_keywords) >= 4:
            score = 25.0  # Well controlled / documented -> LOW risk
        elif len(found_keywords) >= 2:
            score = 42.0  # Moderately documented -> MEDIUM risk
        else:
            score = 55.0  # Sparsely documented -> MEDIUM risk

        risk_level = cls.map_score_to_level(score)
        confidence = min(1.0, 0.4 + (len(found_keywords) * 0.12))

        # Top references
        top_refs = relevant_chunks[:3] if relevant_chunks else evidence_chunks[:3]

        reasoning = (
            f"{cls.agent_name} evaluated {len(evidence_chunks)} evidence chunks. "
            f"Found {len(found_keywords)} domain indicators: {', '.join(list(found_keywords)[:4]) or 'none'}. "
            f"Negative risk indicators detected: {negative_hits}. "
            f"Assigned {cls.dimension} risk score of {score:.1f} ({risk_level})."
        )

        return AgentFinding(
            agent_name=cls.agent_name,
            dimension=cls.dimension,
            score=round(score, 1),
            risk_level=risk_level,
            evidence_references=top_refs,
            missing_information=missing_keywords[:5],
            reasoning_summary=reasoning,
            confidence=round(confidence, 2),
            status="ANALYZED",
        )

