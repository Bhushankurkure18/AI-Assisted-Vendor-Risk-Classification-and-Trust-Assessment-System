"""
Dataset Validation and Preprocessing Pipeline Runner for MFG006.

Verifies:
1. Dataset shape, target distribution, missing values, duplicates.
2. Stratified 80/20 train/test split.
3. ColumnTransformer fit on X_train only (no data leakage).
4. Transformation of train and test sets.
5. Saving of models/mfg006_preprocessor.joblib and models/mfg006_feature_metadata.json.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
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
    ALL_MODEL_FEATURES,
    build_preprocessor_pipeline,
    load_and_prepare_mfg006_data,
    load_and_split_mfg006_data,
    save_preprocessor_and_metadata
)

def run_validation_and_pipeline():
    print("=" * 70)
    print("PHASE 1: MFG006 DATASET VALIDATION")
    print("=" * 70)

    # 1. Load raw dataset
    df = pd.read_csv(RAW_DATA_PATH)
    n_rows, n_cols = df.shape
    n_dupes = df.duplicated().sum()

    print(f"Dataset path         : {RAW_DATA_PATH}")
    print(f"Total rows           : {n_rows}")
    print(f"Total columns        : {n_cols}")
    print(f"Duplicate rows       : {n_dupes}")

    # Target checks
    assert TARGET_COLUMN in df.columns, f"Target '{TARGET_COLUMN}' missing!"
    target_series = df[TARGET_COLUMN].astype(str).str.strip().str.lower()
    unique_classes = sorted(target_series.unique().tolist())
    counts = target_series.value_counts()[TARGET_CLASSES]
    pcts = (target_series.value_counts(normalize=True)[TARGET_CLASSES] * 100).round(2)

    print(f"\nTarget Column        : '{TARGET_COLUMN}'")
    print(f"Target Unique Classes: {unique_classes}")
    assert set(unique_classes) == set(TARGET_CLASSES), f"Classes mismatch: {unique_classes} vs {TARGET_CLASSES}"

    print("\nTarget Class Distribution:")
    for cls in TARGET_CLASSES:
        print(f"  - {cls:<10}: {counts[cls]:>5} ({pcts[cls]:>5.2f}%)")

    # Column types in raw 40 pre-disruption features
    print(f"\nPre-Disruption Features Selected: {len(RAW_PRE_DISRUPTION_FEATURES)}")
    print(f"  - Numerical  : {len(NUMERICAL_FEATURES)}")
    print(f"  - Categorical: {len(CATEGORICAL_FEATURES)}")
    print(f"  - Boolean    : {len(BOOLEAN_FEATURES)}")

    # Missing values in selected features
    missing_in_selected = df[RAW_PRE_DISRUPTION_FEATURES].isna().sum().sum()
    print(f"Missing values in 40 selected features: {missing_in_selected}")
    assert missing_in_selected == 0, "Selected features contain unexpected missing values!"

    print("\n" + "=" * 70)
    print("PHASE 3: STRATIFIED SPLIT & PREPROCESSING PIPELINE")
    print("=" * 70)

    # 2. Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = load_and_split_mfg006_data(
        test_size=0.20,
        random_state=42,
        apply_engineering=True
    )

    print(f"X_train shape: {X_train.shape} (80%)")
    print(f"X_test shape : {X_test.shape} (20%)")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape : {y_test.shape}")
    assert len(X_train) == 2400
    assert len(X_test) == 600

    # Verify class stratification
    print("\nClass Stratification Verification:")
    print("Class      | Train Count (Pct)     | Test Count (Pct)")
    print("-----------+-----------------------+---------------------")
    for idx, cls in enumerate(TARGET_CLASSES):
        tr_cnt = (y_train == idx).sum()
        tr_pct = tr_cnt / len(y_train) * 100
        te_cnt = (y_test == idx).sum()
        te_pct = te_cnt / len(y_test) * 100
        print(f"{cls:<10} | {tr_cnt:>4} ({tr_pct:>5.2f}%)        | {te_cnt:>3} ({te_pct:>5.2f}%)")
        assert abs(tr_pct - te_pct) < 0.5, f"Stratification deviation too high for class {cls}"

    # 3. Build ColumnTransformer pipeline
    print("\nBuilding ColumnTransformer pipeline...")
    preprocessor = build_preprocessor_pipeline()

    # Fit STRICTLY on X_train
    print("Fitting ColumnTransformer STRICTLY on X_train (Zero Data Leakage)...")
    preprocessor.fit(X_train)

    # Transform both splits
    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    print(f"X_train transformed shape: {X_train_trans.shape}")
    print(f"X_test transformed shape : {X_test_trans.shape}")
    assert X_train_trans.shape[0] == 2400
    assert X_test_trans.shape[0] == 600
    assert X_train_trans.shape[1] == X_test_trans.shape[1]
    assert not np.isnan(X_train_trans).any(), "NaN found in transformed X_train!"
    assert not np.isnan(X_test_trans).any(), "NaN found in transformed X_test!"

    # 4. Save preprocessor and feature metadata
    print("\nSaving preprocessor and metadata artifacts...")
    metadata = save_preprocessor_and_metadata(
        fitted_preprocessor=preprocessor,
        random_state=42,
        test_size=0.20
    )

    print(f"Preprocessor saved to: {BASE_DIR / 'models' / 'mfg006_preprocessor.joblib'}")
    print(f"Metadata saved to    : {BASE_DIR / 'models' / 'mfg006_feature_metadata.json'}")
    print(f"Transformed features : {metadata['transformed_feature_count']}")

    print("\n" + "=" * 70)
    print("DATASET VALIDATION & PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_validation_and_pipeline()
