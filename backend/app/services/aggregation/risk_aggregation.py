"""
Risk Aggregation Service combining Phase 1 Quantitative scoring with Phase 2 Agentic scoring.
"""
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.schemas.agent import AgentFinding


class RiskAggregationService:
    """
    Combines Phase 1 rule-based/ML quantitative scores with Phase 2 evidence-grounded agent scores:
    Final Score = (alpha * Phase1_score) + (beta * Phase2_score)
    """

    DEFAULT_DIMENSION_WEIGHTS = {
        "Financial": settings.WEIGHT_FINANCIAL,         # 0.25
        "Security": settings.WEIGHT_SECURITY,           # 0.25
        "Compliance": settings.WEIGHT_COMPLIANCE,       # 0.20
        "Operational": settings.WEIGHT_OPERATIONAL,     # 0.20
        "Reputation": settings.WEIGHT_REPUTATION,       # 0.10
    }

    @classmethod
    def map_score_to_level(cls, score: float) -> str:
        """
        Phase 1 Threshold mapping:
        0 - 39: LOW
        40 - 69: MEDIUM
        70 - 100: HIGH
        """
        if score <= settings.THRESHOLD_LOW_MAX:
            return "LOW"
        elif score <= settings.THRESHOLD_MEDIUM_MAX:
            return "MEDIUM"
        else:
            return "HIGH"

    @classmethod
    def aggregate(
        cls,
        phase1_score: float,
        findings: List[AgentFinding],
        weights: Optional[Dict[str, float]] = None,
        alpha: float = 0.5,
        beta: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Calculates Phase 2 weighted dimension score and combines it with Phase 1 score.
        """
        dimension_weights = weights or cls.DEFAULT_DIMENSION_WEIGHTS
        dimension_scores: Dict[str, float] = {}

        for f in findings:
            dimension_scores[f.dimension] = f.score

        # Default any missing dimension to 50.0 baseline
        for dim in dimension_weights.keys():
            if dim not in dimension_scores:
                dimension_scores[dim] = 50.0

        phase2_weighted = sum(
            dimension_scores[dim] * dimension_weights.get(dim, 0.2)
            for dim in dimension_weights.keys()
        )

        # Normalize alpha & beta to sum to 1.0 if not zero
        total_weight = alpha + beta
        if total_weight > 0:
            norm_alpha = alpha / total_weight
            norm_beta = beta / total_weight
        else:
            norm_alpha = 0.5
            norm_beta = 0.5

        final_score = (norm_alpha * phase1_score) + (norm_beta * phase2_weighted)
        final_score = max(0.0, min(100.0, final_score))
        risk_level = cls.map_score_to_level(final_score)

        return {
            "phase1_score": round(phase1_score, 2),
            "phase2_score": round(phase2_weighted, 2),
            "final_score": round(final_score, 2),
            "risk_level": risk_level,
            "financial_score": round(dimension_scores.get("Financial", 50.0), 2),
            "cybersecurity_score": round(dimension_scores.get("Security", 50.0), 2),
            "compliance_score": round(dimension_scores.get("Compliance", 50.0), 2),
            "operational_score": round(dimension_scores.get("Operational", 50.0), 2),
            "reputation_score": round(dimension_scores.get("Reputation", 50.0), 2),
        }

