"""
Machine Learning Inference and Explainability Service for MFG006.

Loads saved preprocessor and models from disk (Zero retraining on startup).
Generates predictions, class probabilities, Expected Severity Index (ESI),
and feature attribution explanations.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost

from ml.mfg006_preprocessing import (
    RAW_PRE_DISRUPTION_FEATURES,
    TARGET_CLASSES,
    LABEL_MAP,
    INV_LABEL_MAP,
    MODELS_DIR,
    BASE_DIR
)
from backend.app.services.mfg006_preprocessing import MFG006PreprocessingService

RF_MODEL_PATH = MODELS_DIR / "mfg006_random_forest.joblib"
XGB_MODEL_PATH = MODELS_DIR / "mfg006_xgboost.joblib"
METADATA_PATH = MODELS_DIR / "mfg006_feature_metadata.json"
FEATURE_IMP_PATH = BASE_DIR / "reports" / "mfg006_feature_importance.csv"


class MFG006MLService:
    _rf_model = None
    _xgb_model = None
    _metadata = None
    _feature_importance_df = None

    @classmethod
    def load_model(cls, model_name: str = "XGBoost"):
        """
        Load model binary from disk if not already in memory.
        """
        norm_name = model_name.lower().replace(" ", "_").replace("-", "_")

        if "xgb" in norm_name:
            if cls._xgb_model is None:
                if not XGB_MODEL_PATH.exists():
                    raise FileNotFoundError(f"Trained XGBoost model not found at {XGB_MODEL_PATH}")
                cls._xgb_model = joblib.load(XGB_MODEL_PATH)
            return cls._xgb_model, "XGBoost Classifier v1.0"
        elif "random_forest" in norm_name or "rf" in norm_name:
            if cls._rf_model is None:
                if not RF_MODEL_PATH.exists():
                    raise FileNotFoundError(f"Trained Random Forest model not found at {RF_MODEL_PATH}")
                cls._rf_model = joblib.load(RF_MODEL_PATH)
            return cls._rf_model, "Random Forest Classifier v1.0"
        else:
            raise ValueError(f"Unknown model name '{model_name}'. Supported: 'XGBoost', 'Random Forest'")

    @classmethod
    def get_feature_importance_df(cls) -> pd.DataFrame:
        if cls._feature_importance_df is None:
            if FEATURE_IMP_PATH.exists():
                cls._feature_importance_df = pd.read_csv(FEATURE_IMP_PATH)
            else:
                cls._feature_importance_df = pd.DataFrame()
        return cls._feature_importance_df

    @classmethod
    def predict(cls, record: Dict[str, Any], model_name: str = "XGBoost") -> Dict[str, Any]:
        """
        Run inference on pre-disruption input dictionary.
        """
        model, model_label = cls.load_model(model_name)
        X_trans = MFG006PreprocessingService.transform_record(record)

        # Generate predicted class index
        pred_idx = int(model.predict(X_trans)[0])
        pred_label = INV_LABEL_MAP.get(pred_idx, "unknown")

        # Softmax class probabilities
        probs_dict = {}
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_trans)[0]
            for idx, c in enumerate(TARGET_CLASSES):
                probs_dict[c] = round(float(probs[idx]), 4)
        else:
            probs_dict = {c: (1.0 if c == pred_label else 0.0) for c in TARGET_CLASSES}

        # Expected Severity Index (ESI): weighted sum from 1.0 (Low) to 4.0 (Critical)
        esi = round(
            1.0 * probs_dict.get("low", 0.0) +
            2.0 * probs_dict.get("medium", 0.0) +
            3.0 * probs_dict.get("high", 0.0) +
            4.0 * probs_dict.get("critical", 0.0),
            2
        )

        return {
            "predicted_risk": pred_label,
            "probabilities": probs_dict,
            "expected_severity_index": esi,
            "model": model_label,
            "model_version": "1.0.0"
        }

    @classmethod
    def explain(cls, record: Dict[str, Any], model_name: str = "XGBoost") -> Dict[str, Any]:
        """
        Generate feature attribution explanation for the prediction.
        """
        pred_res = cls.predict(record, model_name=model_name)
        predicted_risk = pred_res["predicted_risk"]

        fi_df = cls.get_feature_importance_df()
        contributing_features: List[Dict[str, Any]] = []
        explanation_points: List[str] = []

        if not fi_df.empty:
            top_features = fi_df.head(5)
            for idx, row in top_features.iterrows():
                feat_raw = row["feature"]
                clean_name = feat_raw.replace("num__", "").replace("cat__", "").replace("bool__", "")
                val = record.get(clean_name, "N/A")

                # Determine direction: e.g. low buffer is a risk driver, high buffer is a buffer
                direction = "Risk Driver"
                if clean_name == "inventory_buffer_days_at_onset" and isinstance(val, (int, float)) and val > 45:
                    direction = "Resilience Buffer"
                elif clean_name == "number_of_alternative_suppliers" and isinstance(val, (int, float)) and val >= 2:
                    direction = "Resilience Buffer"
                elif clean_name == "dual_source_in_place" and val is True:
                    direction = "Resilience Buffer"

                contributing_features.append({
                    "feature": feat_raw,
                    "clean_name": clean_name,
                    "value": val,
                    "importance_rank": idx + 1,
                    "global_importance_score": round(float(row["mean_importance"]), 4),
                    "direction": direction
                })

        # Formulate contextual narrative points
        explanation_points.append(
            f"The {pred_res['model']} classified this disruption scenario as '{predicted_risk.upper()}' "
            f"severity with an Expected Severity Index of {pred_res['expected_severity_index']:.2f}/4.0."
        )

        buf = record.get("inventory_buffer_days_at_onset", 0)
        lead = record.get("normal_lead_time_days", 1)
        conc = record.get("supplier_concentration_pct", 0)
        alts = record.get("number_of_alternative_suppliers", 0)

        if conc >= 70 and alts == 0:
            explanation_points.append(
                f"Elevated risk: High supplier concentration ({conc}%) with 0 alternative suppliers creates single-source vulnerability."
            )
        if buf < 15:
            explanation_points.append(
                f"Elevated risk: Inventory buffer ({buf} days) provides inadequate coverage against normal lead times ({lead} days)."
            )
        elif buf >= 45:
            explanation_points.append(
                f"Resilience asset: Substantial buffer inventory ({buf} days) absorbs potential logistics or manufacturing delays."
            )

        fin = record.get("supplier_financial_health_score", 5)
        if fin < 4.0:
            explanation_points.append(
                f"Elevated risk: Supplier financial health score ({fin}/10) indicates high vulnerability to commercial insolvency."
            )

        return {
            "predicted_risk": predicted_risk,
            "probabilities": pred_res["probabilities"],
            "model": pred_res["model"],
            "important_contributing_features": contributing_features,
            "explanation": explanation_points,
            "limitation": "Feature importance identifies statistical tree-split associations in training data; it does not constitute deterministic physical causation."
        }

    @classmethod
    def get_health_status(cls) -> Dict[str, Any]:
        """
        Check health of models, preprocessor, and dependencies.
        """
        rf_exists = RF_MODEL_PATH.exists()
        xgb_exists = XGB_MODEL_PATH.exists()
        prep_exists = MFG006PreprocessingService._preprocessor is not None or (MODELS_DIR / "mfg006_preprocessor.joblib").exists()

        available_models = []
        if rf_exists:
            available_models.append("Random Forest")
        if xgb_exists:
            available_models.append("XGBoost")

        is_healthy = rf_exists and xgb_exists and prep_exists

        return {
            "status": "healthy" if is_healthy else "degraded",
            "preprocessor_loaded": prep_exists,
            "models_available": available_models,
            "total_pre_disruption_features": len(RAW_PRE_DISRUPTION_FEATURES),
            "target_classes": TARGET_CLASSES,
            "library_versions": {
                "scikit-learn": sklearn.__version__,
                "xgboost": xgboost.__version__,
                "joblib": joblib.__version__,
                "pandas": pd.__version__,
                "numpy": np.__version__
            }
        }
