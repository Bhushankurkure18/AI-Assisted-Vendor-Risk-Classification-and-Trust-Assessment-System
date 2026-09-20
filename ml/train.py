"""
Model Training Script for Random Forest and XGBoost.
Saves trained models to models/ directory.
"""
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from ml.preprocessing import load_and_split_data

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def train_models():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print("[TRAIN] Loading and preparing dataset...")
    X_train, X_test, y_train, y_test = load_and_split_data()

    print(f"[TRAIN] Training set size: {len(X_train)} samples, Test set size: {len(X_test)} samples")

    # 1. Random Forest Classifier
    print("[TRAIN] Training Random Forest Classifier...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42,
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    rf_path = MODELS_DIR / "random_forest.pkl"
    joblib.dump(rf, rf_path)
    print(f"[TRAIN] Saved Random Forest model to: {rf_path}")

    # 2. XGBoost Classifier
    print("[TRAIN] Training XGBoost Classifier...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss"
    )
    xgb_model.fit(X_train, y_train)
    xgb_path = MODELS_DIR / "xgboost.pkl"
    joblib.dump(xgb_model, xgb_path)
    print(f"[TRAIN] Saved XGBoost model to: {xgb_path}")

    return rf, xgb_model


if __name__ == "__main__":
    train_models()
