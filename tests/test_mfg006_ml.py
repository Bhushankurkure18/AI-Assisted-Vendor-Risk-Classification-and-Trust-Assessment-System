"""
Comprehensive Automated Test Suite for MFG006 Disruption Machine Learning Pipeline.

Covers all 18 validation criteria:
1. Dataset loading
2. Target existence
3. Leakage-column exclusion
4. Feature metadata
5. Train/test split
6. Preprocessing
7. Unknown categorical values
8. Feature engineering
9. Rule-based prediction
10. Random Forest prediction
11. XGBoost prediction
12. Probability sums
13. Correct output class names
14. Saved artifact loading
15. FastAPI /health
16. FastAPI /predict
17. Invalid API input
18. Missing API input & risk explanation
"""
import pytest
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from ml.mfg006_preprocessing import (
    RAW_DATA_PATH,
    TARGET_COLUMN,
    TARGET_CLASSES,
    LABEL_MAP,
    INV_LABEL_MAP,
    RAW_PRE_DISRUPTION_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
    MODELS_DIR,
    PREPROCESSOR_PATH,
    METADATA_PATH,
    load_and_prepare_mfg006_data,
    load_and_split_mfg006_data,
    add_engineered_features,
    build_preprocessor_pipeline
)
from ml.rule_based_baseline import RuleBasedBaselineClassifier
from backend.app.services.mfg006_ml_service import MFG006MLService, RF_MODEL_PATH, XGB_MODEL_PATH

client = TestClient(app)


# 1. Dataset Loading
def test_dataset_loading():
    assert RAW_DATA_PATH.exists(), f"MFG006 CSV missing at {RAW_DATA_PATH}"
    df = pd.read_csv(RAW_DATA_PATH)
    assert df.shape[0] == 3000, f"Expected 3000 rows, got {df.shape[0]}"
    assert df.shape[1] == 113, f"Expected 113 columns, got {df.shape[1]}"
    assert df.duplicated().sum() == 0, "Encountered unexpected duplicate rows"


# 2. Target Existence & Class Order
def test_target_existence_and_classes():
    df = pd.read_csv(RAW_DATA_PATH)
    assert TARGET_COLUMN in df.columns, f"Target '{TARGET_COLUMN}' missing from dataset"
    raw_classes = set(df[TARGET_COLUMN].astype(str).str.strip().str.lower().unique())
    expected_classes = set(TARGET_CLASSES)
    assert raw_classes == expected_classes, f"Target classes mismatch: {raw_classes} vs {expected_classes}"
    assert df[TARGET_COLUMN].isna().sum() == 0, "Target column contains missing values"


# 3. Leakage Column Exclusion
def test_leakage_column_exclusion():
    leakage_examples = [
        "actual_revenue_loss_usd",
        "stockout_occurred",
        "stockout_duration_days",
        "production_lines_halted",
        "production_lines_throttled",
        "throughput_loss_units",
        "cost_of_disruption_total_usd",
        "post_event_supplier_status",
        "time_to_50pct_recovery_days",
        "time_to_full_recovery_days",
        "recovery_trajectory",
        "insurance_payout_usd",
        "severity_score",
        "event_id",
        "sku"
    ]
    for leak_col in leakage_examples:
        assert leak_col not in RAW_PRE_DISRUPTION_FEATURES, f"CRITICAL LEAKAGE: '{leak_col}' found in model features!"


# 4. Feature Metadata File Integrity
def test_feature_metadata_integrity():
    assert METADATA_PATH.exists(), f"Metadata JSON missing at {METADATA_PATH}"
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["target_column"] == TARGET_COLUMN
    assert meta["target_classes"] == TARGET_CLASSES
    assert meta["raw_feature_count"] == 40
    assert len(meta["engineered_features"]) == 4
    assert meta["total_input_feature_count"] == 44
    assert meta["transformed_feature_count"] == 151


# 5. Train / Test Split & Stratification
def test_train_test_split_stratification():
    X_train, X_test, y_train, y_test = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    assert len(X_train) == 2400
    assert len(X_test) == 600

    for idx, cls in enumerate(TARGET_CLASSES):
        tr_pct = (y_train == idx).sum() / len(y_train) * 100
        te_pct = (y_test == idx).sum() / len(y_test) * 100
        assert abs(tr_pct - te_pct) < 1.0, f"Stratification deviation too high for class {cls}"


# 6. Preprocessing Pipeline Transformation
def test_preprocessing_pipeline_fit_and_transform():
    X_train, X_test, y_train, y_test = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    preprocessor = build_preprocessor_pipeline()
    preprocessor.fit(X_train)

    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    assert X_train_trans.shape == (2400, 151)
    assert X_test_trans.shape == (600, 151)
    assert not np.isnan(X_train_trans).any(), "NaN values found in transformed X_train"
    assert not np.isnan(X_test_trans).any(), "NaN values found in transformed X_test"


# 7. Unknown Categorical Values Handling
def test_unknown_categorical_values_handling():
    X_train, X_test, _, _ = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    preprocessor = build_preprocessor_pipeline()
    preprocessor.fit(X_train)

    # Create record with completely unknown categorical values
    sample = X_test.iloc[0:1].copy()
    sample["industry_sector"] = "space_mining_unknown_sector"
    sample["supplier_country"] = "ZZ_UNKNOWN_NATION"
    sample["disruption_category"] = "alien_encounter_threat"

    # Must transform gracefully without crashing (handle_unknown='ignore')
    trans = preprocessor.transform(sample)
    assert trans.shape == (1, 151)
    assert not np.isnan(trans).any()


# 8. Feature Engineering Calculations & Zero Division Guard
def test_feature_engineering_calculations():
    sample_df = pd.DataFrame([{
        "normal_lead_time_days": 0.0,  # Zero lead time test
        "inventory_buffer_days_at_onset": 15.0,
        "supplier_concentration_pct": 85.0,
        "number_of_alternative_suppliers": 0,
        "supplier_geographic_risk_score": 8.0,
        "supplier_financial_health_score": 2.0,
        "supplier_audit_score_last": 40.0,
        "months_since_last_audit": 24
    }])

    engineered = add_engineered_features(sample_df)
    # Check buffer_to_lead_time_ratio clamped to lower=1.0 to avoid zero division
    assert engineered["buffer_to_lead_time_ratio"].iloc[0] == 15.0
    # Check single_source_dependency_flag
    assert engineered["single_source_dependency_flag"].iloc[0] == 1
    # Check supplier_risk_index: 8*4 + (10-2)*3.5 + (100-40)*0.25 = 32 + 28 + 15 = 75.0
    assert engineered["supplier_risk_index"].iloc[0] == 75.0
    # Check audit_governance_risk: 24 * (100-40)/100 = 14.4
    assert engineered["audit_governance_risk"].iloc[0] == 14.4


# 9. Rule-Based Baseline Prediction
def test_rule_based_baseline_prediction():
    X_train, X_test, y_train, y_test = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    baseline = RuleBasedBaselineClassifier()
    baseline.fit(X_train, y_train)

    preds = baseline.predict(X_test)
    assert len(preds) == 600
    for p in preds:
        assert p in TARGET_CLASSES

    metrics = baseline.evaluate(X_test, y_test)
    assert metrics["accuracy"] > 0.25  # Meaningful baseline


# 10. Random Forest Prediction & Classes
def test_random_forest_prediction():
    assert RF_MODEL_PATH.exists(), f"Random Forest artifact missing at {RF_MODEL_PATH}"
    rf = joblib.load(RF_MODEL_PATH)
    prep = joblib.load(PREPROCESSOR_PATH)

    _, X_test, _, y_test = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    X_test_trans = prep.transform(X_test)

    preds = rf.predict(X_test_trans)
    assert len(preds) == 600
    assert set(preds).issubset({0, 1, 2, 3})


# 11. XGBoost Prediction & Classes
def test_xgboost_prediction():
    assert XGB_MODEL_PATH.exists(), f"XGBoost artifact missing at {XGB_MODEL_PATH}"
    xgb_model = joblib.load(XGB_MODEL_PATH)
    prep = joblib.load(PREPROCESSOR_PATH)

    _, X_test, _, y_test = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    X_test_trans = prep.transform(X_test)

    preds = xgb_model.predict(X_test_trans)
    assert len(preds) == 600
    assert set(preds).issubset({0, 1, 2, 3})


# 12. Probability Sums to One
def test_probability_sums():
    xgb_model = joblib.load(XGB_MODEL_PATH)
    prep = joblib.load(PREPROCESSOR_PATH)

    _, X_test, _, _ = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    X_test_trans = prep.transform(X_test)

    probs = xgb_model.predict_proba(X_test_trans)
    sums = probs.sum(axis=1)
    np.testing.assert_allclose(sums, 1.0, atol=1e-4)


# 13. Output Class Mapping
def test_correct_output_class_names():
    res = MFG006MLService.predict({}, model_name="XGBoost")
    assert res["predicted_risk"] in TARGET_CLASSES
    for cls in TARGET_CLASSES:
        assert cls in res["probabilities"]


# 14. Saved Artifact Loading
def test_saved_artifact_loading():
    assert RF_MODEL_PATH.exists()
    assert XGB_MODEL_PATH.exists()
    assert PREPROCESSOR_PATH.exists()
    assert METADATA_PATH.exists()


# 15. FastAPI /api/v1/ml/health Endpoint
def test_fastapi_ml_health_endpoint():
    res = client.get("/api/v1/ml/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["preprocessor_loaded"] is True
    assert "XGBoost" in data["models_available"]
    assert "Random Forest" in data["models_available"]


# 16. FastAPI /api/v1/ml/predict Endpoint (Valid Input)
def test_fastapi_ml_predict_endpoint():
    payload = {
        "supplier_tier": 1,
        "supplier_geographic_risk_score": 3.0,
        "number_of_alternative_suppliers": 2,
        "supplier_concentration_pct": 50.0,
        "inventory_buffer_days_at_onset": 30.0,
        "normal_lead_time_days": 40.0,
        "supplier_financial_health_score": 8.0,
        "model_name": "XGBoost"
    }
    res = client.post("/api/v1/ml/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_risk"] in TARGET_CLASSES
    assert "probabilities" in data
    assert len(data["probabilities"]) == 4
    assert 1.0 <= data["expected_severity_index"] <= 4.0


# 17. FastAPI Invalid API Input (Validation Error)
def test_fastapi_ml_invalid_input():
    # Pass string where float is expected and negative days
    payload = {
        "normal_lead_time_days": -10.0,  # Fails ge=1.0 validation
        "supplier_tier": 99              # Fails le=4 validation
    }
    res = client.post("/api/v1/ml/predict", json=payload)
    assert res.status_code == 422  # Pydantic validation error


# 18. FastAPI Risk Explanation Endpoint
def test_fastapi_ml_risk_explanation_endpoint():
    payload = {
        "supplier_concentration_pct": 90.0,
        "number_of_alternative_suppliers": 0,
        "inventory_buffer_days_at_onset": 5.0,
        "normal_lead_time_days": 75.0,
        "model_name": "XGBoost"
    }
    res = client.post("/api/v1/ml/risk-explanation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "important_contributing_features" in data
    assert len(data["important_contributing_features"]) > 0
    assert "explanation" in data
    assert len(data["explanation"]) > 0
    assert "limitation" in data
