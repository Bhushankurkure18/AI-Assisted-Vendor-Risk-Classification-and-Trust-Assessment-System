"""
Data preprocessing service.
Reusable logic for data cleaning, validation, and feature preparation for ML models.
Used consistently in both batch training and real-time API inference.
"""
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np


class PreprocessingService:
    FEATURE_COLUMNS = [
        "financial_score",
        "security_score",
        "compliance_score",
        "operational_score",
        "reputation_score"
    ]

    LABEL_MAP = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2
    }
    INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

    @classmethod
    def validate_and_clean_record(cls, record: Dict[str, Any]) -> Dict[str, float]:
        """
        Validate single vendor record numerical fields and clamp/clean them.
        """
        cleaned: Dict[str, float] = {}
        for col in cls.FEATURE_COLUMNS:
            val = record.get(col)
            if val is None:
                raise ValueError(f"Missing required feature: {col}")
            try:
                num_val = float(val)
            except (ValueError, TypeError):
                raise ValueError(f"Feature {col} must be numeric. Received: {val}")

            if not (0.0 <= num_val <= 100.0):
                raise ValueError(f"Feature {col} value {num_val} outside acceptable range [0, 100]")

            cleaned[col] = num_val
        return cleaned

    @classmethod
    def extract_features_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract clean feature matrix from a dataframe.
        Fills missing numeric values with column medians.
        """
        missing_cols = [c for c in cls.FEATURE_COLUMNS if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Dataframe missing required columns: {missing_cols}")

        X = df[cls.FEATURE_COLUMNS].copy()

        # Handle missing values
        X = X.fillna(X.median(numeric_only=True))

        # Ensure all columns are float
        for col in cls.FEATURE_COLUMNS:
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(50.0).clip(0.0, 100.0)

        return X

    @classmethod
    def prepare_dataset(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Clean and extract features and labels from raw dataframe.
        """
        # Remove duplicates based on vendor_id or vendor_name if present
        if "vendor_id" in df.columns:
            df = df.drop_duplicates(subset=["vendor_id"]).copy()

        X = cls.extract_features_dataframe(df)

        if "risk_label" not in df.columns:
            raise ValueError("Target column 'risk_label' missing from dataset")

        y = df["risk_label"].str.upper().map(cls.LABEL_MAP)
        # Drop unmapped or null labels
        valid_mask = y.notna()
        X = X[valid_mask]
        y = y[valid_mask].astype(int)

        return X, y
