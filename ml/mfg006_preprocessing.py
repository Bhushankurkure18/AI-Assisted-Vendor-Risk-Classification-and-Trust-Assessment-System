"""
MFG006 Disruption Dataset Preprocessing and Pipeline Utilities.

Implements strict zero-target-leakage preprocessing, reproducible train/test
splitting, and scikit-learn ColumnTransformer pipelines for multiclass disruption
severity prediction ('low', 'medium', 'high', 'critical').
"""
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
import joblib

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "mfg006_disruptions.csv"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
PREPROCESSOR_PATH = MODELS_DIR / "mfg006_preprocessor.joblib"
METADATA_PATH = MODELS_DIR / "mfg006_feature_metadata.json"

# Target Specification
TARGET_COLUMN = "severity_level"
TARGET_CLASSES = ["low", "medium", "high", "critical"]
LABEL_MAP = {"low": 0, "medium": 1, "high": 2, "critical": 3}
INV_LABEL_MAP = {0: "low", 1: "medium", 2: "high", 3: "critical"}

# 40 Approved Pre-Disruption Feature Names
NUMERICAL_FEATURES: List[str] = [
    "supplier_tier",
    "supplier_geographic_risk_score",
    "number_of_alternative_suppliers",
    "supplier_concentration_pct",
    "affected_sku_count",
    "supplier_financial_health_score",
    "supplier_audit_score_last",
    "months_since_last_audit",
    "supplier_relationship_years",
    "supply_volume_at_risk_units",
    "revenue_at_risk_usd",
    "inventory_buffer_days_at_onset",
    "normal_lead_time_days",
    "freight_cost_normal_usd",
    "demand_volatility_index",
    "demand_forecast_error_mape",
    "order_variability_bullwhip_ratio",
    "customer_concentration_top3_pct",
    "early_warning_lead_days",
    "supply_chain_visibility_score",
    "supply_chain_maturity_score"
]

CATEGORICAL_FEATURES: List[str] = [
    "industry_sector",
    "disruption_category",
    "disruption_subcategory",
    "affected_region",
    "supplier_criticality",
    "supplier_country",
    "affected_component_category",
    "logistics_mode_primary",
    "logistics_concentration_risk",
    "safety_stock_adequacy",
    "early_warning_source",
    "resilience_posture_pre_event"
]

BOOLEAN_FEATURES: List[str] = [
    "dual_source_in_place",
    "nearshoring_available",
    "early_warning_signal_detected",
    "digital_twin_available",
    "erp_alert_triggered",
    "external_data_feed_active",
    "tier2_visibility_flag"
]

RAW_PRE_DISRUPTION_FEATURES: List[str] = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + BOOLEAN_FEATURES

# Engineered Feature Names (Pre-Disruption Only)
ENGINEERED_NUMERICAL_FEATURES: List[str] = [
    "buffer_to_lead_time_ratio",
    "supplier_risk_index",
    "audit_governance_risk"
]

ENGINEERED_BOOLEAN_FEATURES: List[str] = [
    "single_source_dependency_flag"
]

ALL_NUMERICAL_FEATURES: List[str] = NUMERICAL_FEATURES + ENGINEERED_NUMERICAL_FEATURES
ALL_CATEGORICAL_FEATURES: List[str] = CATEGORICAL_FEATURES
ALL_BOOLEAN_FEATURES: List[str] = BOOLEAN_FEATURES + ENGINEERED_BOOLEAN_FEATURES
ALL_MODEL_FEATURES: List[str] = ALL_NUMERICAL_FEATURES + ALL_CATEGORICAL_FEATURES + ALL_BOOLEAN_FEATURES


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive 4 domain-justified pre-disruption features:
    1. buffer_to_lead_time_ratio: inventory buffer relative to normal lead time.
    2. single_source_dependency_flag: high concentration (>=70%) with 0 alternative suppliers.
    3. supplier_risk_index: composite risk combining geo risk, inverted financial health, and inverted audit score.
    4. audit_governance_risk: time since last audit amplified by audit deficiency.
    """
    df_out = df.copy()

    # 1. buffer_to_lead_time_ratio (Safe division: lower bound lead time to 1.0 day)
    lead_time = pd.to_numeric(df_out["normal_lead_time_days"], errors="coerce").fillna(30.0).clip(lower=1.0)
    buffer_days = pd.to_numeric(df_out["inventory_buffer_days_at_onset"], errors="coerce").fillna(0.0).clip(lower=0.0)
    df_out["buffer_to_lead_time_ratio"] = (buffer_days / lead_time).round(4)

    # 2. single_source_dependency_flag (Boolean int: 1 if single-sourced with >=70% dependency and 0 alternatives)
    concentration = pd.to_numeric(df_out["supplier_concentration_pct"], errors="coerce").fillna(0.0)
    alternatives = pd.to_numeric(df_out["number_of_alternative_suppliers"], errors="coerce").fillna(0)
    df_out["single_source_dependency_flag"] = ((concentration >= 70.0) & (alternatives == 0)).astype(int)

    # 3. supplier_risk_index (Scaled 0 to 100)
    geo_risk = pd.to_numeric(df_out["supplier_geographic_risk_score"], errors="coerce").fillna(5.0).clip(0.0, 10.0)
    fin_health = pd.to_numeric(df_out["supplier_financial_health_score"], errors="coerce").fillna(5.0).clip(0.0, 10.0)
    audit_score = pd.to_numeric(df_out["supplier_audit_score_last"], errors="coerce").fillna(50.0).clip(0.0, 100.0)

    geo_term = geo_risk * 4.0               # Max 40
    fin_term = (10.0 - fin_health) * 3.5    # Max 35
    audit_term = (100.0 - audit_score) * 0.25 # Max 25
    df_out["supplier_risk_index"] = (geo_term + fin_term + audit_term).round(2)

    # 4. audit_governance_risk
    months_audit = pd.to_numeric(df_out["months_since_last_audit"], errors="coerce").fillna(12.0).clip(lower=0.0)
    audit_deficiency = (100.0 - audit_score) / 100.0
    df_out["audit_governance_risk"] = (months_audit * audit_deficiency).round(4)

    return df_out


def _bool_to_int(x):
    """Convert boolean arrays/dataframes to integer 0/1 for modeling."""
    return x.astype(int)


def build_preprocessor_pipeline(
    numerical_cols: Optional[List[str]] = None,
    categorical_cols: Optional[List[str]] = None,
    boolean_cols: Optional[List[str]] = None
) -> ColumnTransformer:
    """
    Build scikit-learn ColumnTransformer.
    - Numerical: Median imputation + RobustScaler (resilient to heavy financial/volume tails).
    - Categorical: Most frequent imputation + OneHotEncoder(handle_unknown='ignore').
    - Boolean: Most frequent imputation + cast to integer.
    """
    num_cols = numerical_cols if numerical_cols is not None else ALL_NUMERICAL_FEATURES
    cat_cols = categorical_cols if categorical_cols is not None else ALL_CATEGORICAL_FEATURES
    bool_cols = boolean_cols if boolean_cols is not None else ALL_BOOLEAN_FEATURES

    numerical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler())
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    boolean_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("to_int", FunctionTransformer(_bool_to_int, feature_names_out="one-to-one"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_pipeline, num_cols),
            ("cat", categorical_pipeline, cat_cols),
            ("bool", boolean_pipeline, bool_cols)
        ],
        remainder="drop"
    )

    return preprocessor


def load_and_prepare_mfg006_data(
    csv_path: Optional[Path] = None,
    apply_engineering: bool = True
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Load raw MFG006 CSV, isolate 40 pre-disruption features, apply feature engineering,
    and encode target severity_level.
    """
    path = csv_path if csv_path is not None else RAW_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"MFG006 dataset not found at: {path}")

    raw_df = pd.read_csv(path)

    # Validate target presence
    if TARGET_COLUMN not in raw_df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' missing from {path}")

    # Validate raw features presence
    missing_features = [f for f in RAW_PRE_DISRUPTION_FEATURES if f not in raw_df.columns]
    if missing_features:
        raise ValueError(f"Dataset missing required pre-disruption features: {missing_features}")

    # Extract X and normalize boolean/numeric types
    X_raw = raw_df[RAW_PRE_DISRUPTION_FEATURES].copy()

    # Normalize boolean columns
    for b_col in BOOLEAN_FEATURES:
        X_raw[b_col] = X_raw[b_col].astype(bool)

    # Normalize categorical string columns
    for c_col in CATEGORICAL_FEATURES:
        X_raw[c_col] = X_raw[c_col].astype(str).str.strip()

    # Normalize numerical columns
    for n_col in NUMERICAL_FEATURES:
        X_raw[n_col] = pd.to_numeric(X_raw[n_col], errors="coerce")

    # Apply feature engineering
    if apply_engineering:
        X = add_engineered_features(X_raw)
    else:
        X = X_raw

    # Target normalization & mapping
    y_raw = raw_df[TARGET_COLUMN].astype(str).str.strip().str.lower()
    y = y_raw.map(LABEL_MAP)

    if y.isna().any():
        invalid_labels = raw_df.loc[y.isna(), TARGET_COLUMN].unique().tolist()
        raise ValueError(f"Encountered unexpected target labels: {invalid_labels}")

    y = y.astype(int)

    return X, y, raw_df


def load_and_split_mfg006_data(
    test_size: float = 0.20,
    random_state: int = 42,
    apply_engineering: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Reproducible stratified 80/20 train/test split.
    Guarantees zero target leakage and exact class stratification.
    """
    X, y, _ = load_and_prepare_mfg006_data(apply_engineering=apply_engineering)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


def save_preprocessor_and_metadata(
    fitted_preprocessor: ColumnTransformer,
    random_state: int = 42,
    test_size: float = 0.20
) -> Dict[str, Any]:
    """
    Save fitted preprocessor and feature metadata to disk for reproducible reuse.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Save preprocessor binary
    joblib.dump(fitted_preprocessor, PREPROCESSOR_PATH)

    # 2. Extract transformed feature names
    try:
        transformed_feature_names = fitted_preprocessor.get_feature_names_out().tolist()
    except Exception:
        transformed_feature_names = []

    # 3. Create metadata dictionary
    metadata = {
        "dataset_name": "MFG006 Disruption Dataset",
        "dataset_file": "mfg006_disruptions.csv",
        "target_column": TARGET_COLUMN,
        "target_classes": TARGET_CLASSES,
        "label_map": LABEL_MAP,
        "inv_label_map": {str(k): v for k, v in INV_LABEL_MAP.items()},
        "raw_pre_disruption_features": RAW_PRE_DISRUPTION_FEATURES,
        "raw_feature_count": len(RAW_PRE_DISRUPTION_FEATURES),
        "engineered_features": ENGINEERED_NUMERICAL_FEATURES + ENGINEERED_BOOLEAN_FEATURES,
        "all_model_features": ALL_MODEL_FEATURES,
        "total_input_feature_count": len(ALL_MODEL_FEATURES),
        "numerical_features": ALL_NUMERICAL_FEATURES,
        "categorical_features": ALL_CATEGORICAL_FEATURES,
        "boolean_features": ALL_BOOLEAN_FEATURES,
        "train_test_split": {
            "test_size": test_size,
            "train_size": 1.0 - test_size,
            "stratified": True,
            "random_state": random_state
        },
        "scaler": "RobustScaler (IQR based, robust to long-tail financial & lead-time variables)",
        "imputer_numerical": "SimpleImputer(strategy='median')",
        "imputer_categorical": "SimpleImputer(strategy='most_frequent')",
        "encoder": "OneHotEncoder(handle_unknown='ignore', sparse_output=False)",
        "transformed_feature_count": len(transformed_feature_names),
        "transformed_feature_names": transformed_feature_names
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata
