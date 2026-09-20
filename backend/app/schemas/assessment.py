"""
Assessment Pydantic schemas.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional


class AssessmentBase(BaseModel):
    rule_based_score: float
    rule_based_level: str
    ml_prediction: str
    ml_model: str


class AssessmentResponse(AssessmentBase):
    assessment_id: int
    vendor_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VendorSummary(BaseModel):
    id: int
    name: str


class RuleBasedAssessmentResult(BaseModel):
    score: float
    risk_level: str
    category_scores: Dict[str, float]
    key_risk_factors: List[str] = Field(default_factory=list)


class MLAssessmentResult(BaseModel):
    model: str
    prediction: str
    probabilities: Optional[Dict[str, float]] = None


class CombinedAssessmentResponse(BaseModel):
    vendor: VendorSummary
    rule_based_assessment: RuleBasedAssessmentResult
    ml_assessment: MLAssessmentResult
    explanation: List[str]
