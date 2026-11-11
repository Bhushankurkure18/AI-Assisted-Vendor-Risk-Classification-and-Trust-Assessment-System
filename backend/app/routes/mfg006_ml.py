"""
FastAPI Routes for MFG006 Disruption Severity Machine Learning.

Exposes:
- GET  /api/v1/ml/health
- POST /api/v1/ml/predict
- POST /api/v1/ml/risk-explanation
"""
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.ml_prediction import (
    MFG006PredictRequest,
    MFG006PredictResponse,
    MFG006ExplanationResponse,
    MLHealthResponse
)
from backend.app.services.mfg006_ml_service import MFG006MLService

router = APIRouter(prefix="/api/v1/ml", tags=["MFG006 Machine Learning"])


@router.get("/health", response_model=MLHealthResponse)
def get_ml_health():
    """
    Check availability of trained models, preprocessor, and ML libraries.
    Does not expose secrets.
    """
    status_data = MFG006MLService.get_health_status()
    return status_data


@router.post("/predict", response_model=MFG006PredictResponse)
def predict_disruption_severity(request: MFG006PredictRequest):
    """
    Predict disruption severity level using pre-disruption features.
    Strictly zero target leakage: only pre-disruption variables accepted.
    """
    try:
        model_name = request.model_name or "XGBoost"
        payload = request.model_dump()
        result = MFG006MLService.predict(payload, model_name=model_name)
        return result
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model artifact not loaded: {str(fnf_err)}"
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal prediction error: {str(exc)}"
        )


@router.post("/risk-explanation", response_model=MFG006ExplanationResponse)
def explain_disruption_risk(request: MFG006PredictRequest):
    """
    Generate feature attribution and contextual risk explanation for a vendor scenario.
    """
    try:
        model_name = request.model_name or "XGBoost"
        payload = request.model_dump()
        result = MFG006MLService.explain(payload, model_name=model_name)
        return result
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model artifact not loaded: {str(fnf_err)}"
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal explanation error: {str(exc)}"
        )
