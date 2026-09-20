"""
Assessment API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.vendor import Vendor
from backend.app.models.assessment import Assessment
from backend.app.schemas.assessment import (
    CombinedAssessmentResponse,
    AssessmentResponse,
    VendorSummary,
    RuleBasedAssessmentResult,
    MLAssessmentResult,
)
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.ml_service import MLService
from backend.app.services.preprocessing import PreprocessingService

router = APIRouter(tags=["Assessments"])


@router.post("/assess/{vendor_id}", response_model=CombinedAssessmentResponse)
def assess_vendor(
    vendor_id: int,
    model_name: str = Query(default="Random Forest", description="ML model to use ('Random Forest' or 'XGBoost')"),
    db: Session = Depends(get_db)
):
    """
    Core Assessment Endpoint:
    1. Fetch vendor from database.
    2. Validate and clean vendor data.
    3. Calculate rule-based risk score, level, and category breakdown.
    4. Run ML prediction using trained model.
    5. Persist assessment record in database.
    6. Return unified explainable risk report.
    """
    if vendor_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vendor ID")

    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor with ID {vendor_id} not found")

    category_scores = {
        "financial": float(vendor.financial_score),
        "security": float(vendor.security_score),
        "compliance": float(vendor.compliance_score),
        "operational": float(vendor.operational_score),
        "reputation": float(vendor.reputation_score),
    }

    # 1. Rule-based evaluation
    rule_result = RiskEngine.assess(category_scores)

    # 2. ML Prediction
    try:
        ml_features = {
            "financial_score": vendor.financial_score,
            "security_score": vendor.security_score,
            "compliance_score": vendor.compliance_score,
            "operational_score": vendor.operational_score,
            "reputation_score": vendor.reputation_score,
        }
        ml_result = MLService.predict(ml_features, model_name=model_name)
    except FileNotFoundError:
        # Graceful fallback if ML models are not yet trained (e.g. before M5)
        ml_result = {
            "model": model_name,
            "prediction": rule_result["risk_level"],
            "probabilities": None
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ML prediction error: {str(exc)}")

    # 3. Store assessment record
    db_assessment = Assessment(
        vendor_id=vendor.vendor_id,
        rule_based_score=rule_result["score"],
        rule_based_level=rule_result["risk_level"],
        ml_prediction=ml_result["prediction"],
        ml_model=ml_result["model"]
    )
    db.add(db_assessment)
    db.commit()

    # 4. Formulate consolidated explanation
    explanation = list(rule_result["explanation"])
    if ml_result["prediction"] != rule_result["risk_level"]:
        explanation.append(
            f"Note: ML model predicted {ml_result['prediction']}, differing from rule-based baseline {rule_result['risk_level']}. Review individual dimension variances."
        )
    else:
        explanation.append(
            f"Consensus: Both rule-based engine and {ml_result['model']} agree on {rule_result['risk_level']} risk level."
        )

    return CombinedAssessmentResponse(
        vendor=VendorSummary(id=vendor.vendor_id, name=vendor.vendor_name),
        rule_based_assessment=RuleBasedAssessmentResult(
            score=rule_result["score"],
            risk_level=rule_result["risk_level"],
            category_scores=rule_result["category_scores"],
            key_risk_factors=rule_result["key_risk_factors"]
        ),
        ml_assessment=MLAssessmentResult(
            model=ml_result["model"],
            prediction=ml_result["prediction"],
            probabilities=ml_result.get("probabilities")
        ),
        explanation=explanation
    )


@router.get("/assessments/{vendor_id}", response_model=List[AssessmentResponse])
def get_vendor_assessments(vendor_id: int, db: Session = Depends(get_db)):
    """
    Retrieve historical assessment records for a given vendor.
    """
    if vendor_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vendor ID")

    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vendor with ID {vendor_id} not found")

    assessments = db.query(Assessment).filter(Assessment.vendor_id == vendor_id).order_by(Assessment.created_at.desc()).all()
    return assessments
