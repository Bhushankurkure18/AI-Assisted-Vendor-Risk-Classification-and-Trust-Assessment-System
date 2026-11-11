"""
Backend Service for MFG006 Preprocessing and Feature Preparation.

Provides single-record validation, feature cleaning, feature engineering,
and transformation using the pre-fitted scikit-learn ColumnTransformer.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import pandas as pd
import numpy as np

from ml.mfg006_preprocessing import (
    RAW_PRE_DISRUPTION_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
    ALL_MODEL_FEATURES,
    TARGET_CLASSES,
    LABEL_MAP,
    INV_LABEL_MAP,
    PREPROCESSOR_PATH,
    METADATA_PATH,
    add_engineered_features
)


class MFG006PreprocessingService:
    """
    Service wrapper for production inference and input validation.
    """
    _preprocessor = None

    @classmethod
    def get_preprocessor(cls):
        """
        Lazy-load the fitted ColumnTransformer from disk.
        """
        if cls._preprocessor is None:
            if not PREPROCESSOR_PATH.exists():
                raise FileNotFoundError(
                    f"MFG006 preprocessor artifact not found at {PREPROCESSOR_PATH}. "
                    "Run training pipeline first."
                )
            cls._preprocessor = joblib.load(PREPROCESSOR_PATH)
        return cls._preprocessor

    @classmethod
    def validate_and_format_record(cls, record: Dict[str, Any]) -> pd.DataFrame:
        """
        Validate single record input dictionary and return a single-row DataFrame.
        """
        # Ensure all required raw pre-disruption features are present
        row_dict = {}
        for col in RAW_PRE_DISRUPTION_FEATURES:
            if col in record:
                val = record[col]
            else:
                # Fallback to sensible defaults if missing in partial payload
                if col in BOOLEAN_FEATURES:
                    val = False
                elif col in NUMERICAL_FEATURES:
                    val = np.nan
                else:
                    val = "unknown"
            row_dict[col] = [val]

        df_single = pd.DataFrame(row_dict)

        # Cast boolean columns
        for b_col in BOOLEAN_FEATURES:
            df_single[b_col] = df_single[b_col].astype(bool)

        # Cast numerical columns
        for n_col in NUMERICAL_FEATURES:
            df_single[n_col] = pd.to_numeric(df_single[n_col], errors="coerce")

        # Cast categorical columns
        for c_col in CATEGORICAL_FEATURES:
            df_single[c_col] = df_single[c_col].astype(str).str.strip()

        # Apply feature engineering
        df_engineered = add_engineered_features(df_single)

        return df_engineered

    @classmethod
    def transform_record(cls, record: Dict[str, Any]) -> np.ndarray:
        """
        Transform a single record using the fitted preprocessor.
        Returns a 2D numpy array suitable for model.predict().
        """
        preprocessor = cls.get_preprocessor()
        df_engineered = cls.validate_and_format_record(record)
        return preprocessor.transform(df_engineered)
