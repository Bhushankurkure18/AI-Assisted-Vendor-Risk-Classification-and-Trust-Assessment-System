"""
Rule-Based Risk Calculation Engine.
Implements the 5-dimension weighted risk formulation:
- Financial: 25%
- Security: 25%
- Compliance: 20%
- Operational: 20%
- Reputation: 10%

Thresholds (Prototype Implementation):
- 0 to 39: LOW
- 40 to 69: MEDIUM
- 70 to 100: HIGH
"""
from typing import Dict, Any, List
from backend.app.core.config import settings


class RiskEngine:
    @staticmethod
    def calculate_weighted_score(category_scores: Dict[str, float]) -> float:
        """
        Calculate the weighted normalized risk score (0 - 100).
        """
        fin = category_scores.get("financial", 0.0)
        sec = category_scores.get("security", 0.0)
        comp = category_scores.get("compliance", 0.0)
        ops = category_scores.get("operational", 0.0)
        rep = category_scores.get("reputation", 0.0)

        total = (
            fin * settings.WEIGHT_FINANCIAL +
            sec * settings.WEIGHT_SECURITY +
            comp * settings.WEIGHT_COMPLIANCE +
            ops * settings.WEIGHT_OPERATIONAL +
            rep * settings.WEIGHT_REPUTATION
        )
        return round(float(total), 2)

    @staticmethod
    def classify_level(score: float) -> str:
        """
        Classify risk level according to implementation thresholds:
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

    @staticmethod
    def generate_risk_factors_and_explanation(
        category_scores: Dict[str, float], overall_score: float, risk_level: str
    ) -> Dict[str, Any]:
        """
        Generate data-grounded key risk factors and an explainable breakdown.
        """
        key_factors: List[str] = []
        explanation_points: List[str] = []

        threshold_factor = 60.0  # scores >= 60 in individual categories indicate elevated risk

        dim_labels = {
            "financial": "Financial",
            "security": "Security",
            "compliance": "Compliance",
            "operational": "Operational",
            "reputation": "Reputation"
        }

        for dim, label in dim_labels.items():
            val = category_scores.get(dim, 0.0)
            if val >= 70.0:
                key_factors.append(f"Critical {label} risk requires immediate mitigation (score: {val:.1f})")
            elif val >= threshold_factor:
                key_factors.append(f"Elevated {label} risk detected (score: {val:.1f})")

        explanation_points.append(
            f"Overall weighted risk score computed as {overall_score:.2f}/100, placing the vendor in the {risk_level} risk tier."
        )
        explanation_points.append(
            f"Dimension weights applied: Financial (25%), Security (25%), Compliance (20%), Operational (20%), Reputation (10%)."
        )

        if not key_factors:
            explanation_points.append("All risk dimensions are within stable operational boundaries.")
        else:
            explanation_points.append(
                f"Primary risk drivers: {', '.join([k.split(' (score')[0] for k in key_factors])}."
            )

        return {
            "key_risk_factors": key_factors,
            "explanation": explanation_points
        }

    @classmethod
    def assess(cls, category_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform complete rule-based risk evaluation.
        """
        score = cls.calculate_weighted_score(category_scores)
        level = cls.classify_level(score)
        details = cls.generate_risk_factors_and_explanation(category_scores, score, level)

        return {
            "score": score,
            "risk_level": level,
            "category_scores": category_scores,
            "key_risk_factors": details["key_risk_factors"],
            "explanation": details["explanation"]
        }
