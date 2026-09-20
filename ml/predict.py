"""
ML Prediction CLI / Utility.
"""
from backend.app.services.ml_service import MLService
from typing import Dict, Any


def run_prediction(features: Dict[str, float], model_name: str = "Random Forest") -> Dict[str, Any]:
    """
    Run prediction on sample input feature dictionary.
    """
    return MLService.predict(features, model_name=model_name)


if __name__ == "__main__":
    sample_features = {
        "financial_score": 35.0,
        "security_score": 75.0,
        "compliance_score": 45.0,
        "operational_score": 30.0,
        "reputation_score": 25.0
    }
    print("Sample features:", sample_features)
    try:
        res_rf = run_prediction(sample_features, "Random Forest")
        print("Random Forest Prediction:", res_rf)
        res_xgb = run_prediction(sample_features, "XGBoost")
        print("XGBoost Prediction:", res_xgb)
    except FileNotFoundError as e:
        print(f"Prediction note: {e}")
