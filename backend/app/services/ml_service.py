"""
Machine Learning inference service.
Loads saved models (Random Forest / XGBoost) and generates risk predictions.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from backend.app.services.preprocessing import PreprocessingService


class MLService:
    MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "models"
    DEFAULT_MODEL_NAME = "Random Forest"

    _rf_model = None
    _xgb_model = None

    @classmethod
    def load_model(cls, model_name: str = "Random Forest"):
        """
        Load specified model from disk.
        """
        if model_name.lower().replace(" ", "_") == "random_forest" or model_name == "Random Forest":
            path = cls.MODELS_DIR / "random_forest.pkl"
            if not path.exists():
                raise FileNotFoundError(f"Trained Random Forest model not found at {path}. Run training first.")
            if cls._rf_model is None:
                cls._rf_model = joblib.load(path)
            return cls._rf_model
        elif model_name.lower() == "xgboost" or model_name == "XGBoost":
            path = cls.MODELS_DIR / "xgboost.pkl"
            if not path.exists():
                raise FileNotFoundError(f"Trained XGBoost model not found at {path}. Run training first.")
            if cls._xgb_model is None:
                cls._xgb_model = joblib.load(path)
            return cls._xgb_model
        else:
            raise ValueError(f"Unknown model name: {model_name}. Supported: 'Random Forest', 'XGBoost'")

    @classmethod
    def predict(cls, features: Dict[str, float], model_name: str = "Random Forest") -> Dict[str, Any]:
        """
        Run ML prediction using specified model on single vendor features.
        """
        model = cls.load_model(model_name)
        cleaned = PreprocessingService.validate_and_clean_record(features)
        feature_row = pd.DataFrame([[cleaned[col] for col in PreprocessingService.FEATURE_COLUMNS]],
                                   columns=PreprocessingService.FEATURE_COLUMNS)

        pred_idx = int(model.predict(feature_row)[0])
        pred_label = PreprocessingService.INV_LABEL_MAP.get(pred_idx, "UNKNOWN")

        probabilities: Optional[Dict[str, float]] = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(feature_row)[0]
            probabilities = {
                PreprocessingService.INV_LABEL_MAP[i]: round(float(p), 4)
                for i, p in enumerate(probs)
                if i in PreprocessingService.INV_LABEL_MAP
            }

        return {
            "model": model_name,
            "prediction": pred_label,
            "probabilities": probabilities
        }
