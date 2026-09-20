"""
Machine Learning Preprocessing and Dataset Utilities.
Includes synthetic vendor data generation, feature validation, and train/test splitting.
"""
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from backend.app.core.config import settings

RAW_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "vendors.csv"
PROCESSED_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def generate_synthetic_dataset(n_samples: int = 600, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic vendor risk dataset.
    Labeled as SYNTHETIC.
    Columns:
    - vendor_id
    - vendor_name
    - revenue
    - debt
    - financial_score
    - security_score
    - compliance_score
    - operational_score
    - reputation_score
    - risk_label (LOW / MEDIUM / HIGH derived from weighted dimension scores)
    """
    np.random.seed(random_state)

    vendor_prefixes = ["Apex", "Cyber", "Nexus", "Quantum", "Vertex", "Aegis", "Horizon", "Strata", "Vanguard", "Omni"]
    vendor_suffixes = ["Technologies", "Solutions", "Logistics", "Enterprises", "Security", "Systems", "Networks", "Holdings"]

    names = [
        f"{np.random.choice(vendor_prefixes)} {np.random.choice(vendor_suffixes)} #{i+1001}"
        for i in range(n_samples)
    ]

    revenues = np.round(np.random.exponential(scale=5000000, size=n_samples) + 250000, 2)
    debts = np.round(revenues * np.random.uniform(0.1, 0.9, size=n_samples), 2)

    # Risk dimension scores (0 to 100, where higher means higher risk)
    # Generate balanced clusters across Low, Medium, and High
    clusters = np.random.choice(["low_bias", "med_bias", "high_bias"], size=n_samples, p=[0.33, 0.34, 0.33])

    financial_scores = []
    security_scores = []
    compliance_scores = []
    operational_scores = []
    reputation_scores = []

    for c in clusters:
        if c == "low_bias":
            financial_scores.append(np.random.uniform(5, 38))
            security_scores.append(np.random.uniform(5, 38))
            compliance_scores.append(np.random.uniform(5, 38))
            operational_scores.append(np.random.uniform(5, 38))
            reputation_scores.append(np.random.uniform(5, 38))
        elif c == "med_bias":
            financial_scores.append(np.random.uniform(35, 68))
            security_scores.append(np.random.uniform(35, 68))
            compliance_scores.append(np.random.uniform(35, 68))
            operational_scores.append(np.random.uniform(35, 68))
            reputation_scores.append(np.random.uniform(35, 68))
        else:
            financial_scores.append(np.random.uniform(65, 95))
            security_scores.append(np.random.uniform(65, 95))
            compliance_scores.append(np.random.uniform(65, 95))
            operational_scores.append(np.random.uniform(65, 95))
            reputation_scores.append(np.random.uniform(65, 95))

    fin = np.round(np.clip(financial_scores, 0.0, 100.0), 2)
    sec = np.round(np.clip(security_scores, 0.0, 100.0), 2)
    comp = np.round(np.clip(compliance_scores, 0.0, 100.0), 2)
    ops = np.round(np.clip(operational_scores, 0.0, 100.0), 2)
    rep = np.round(np.clip(reputation_scores, 0.0, 100.0), 2)

    # Compute weighted score: 25% Fin, 25% Sec, 20% Comp, 20% Ops, 10% Rep
    weighted_scores = (
        fin * settings.WEIGHT_FINANCIAL +
        sec * settings.WEIGHT_SECURITY +
        comp * settings.WEIGHT_COMPLIANCE +
        ops * settings.WEIGHT_OPERATIONAL +
        rep * settings.WEIGHT_REPUTATION
    )

    # Logical risk labels derived from weighted scores
    risk_labels = []
    for s in weighted_scores:
        if s <= settings.THRESHOLD_LOW_MAX:
            risk_labels.append("LOW")
        elif s <= settings.THRESHOLD_MEDIUM_MAX:
            risk_labels.append("MEDIUM")
        else:
            risk_labels.append("HIGH")

    df = pd.DataFrame({
        "vendor_id": list(range(1, n_samples + 1)),
        "vendor_name": names,
        "revenue": revenues,
        "debt": debts,
        "financial_score": fin,
        "security_score": sec,
        "compliance_score": comp,
        "operational_score": ops,
        "reputation_score": rep,
        "risk_label": risk_labels
    })

    return df


def load_and_split_data(
    test_size: float = 0.2, random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Load raw vendors dataset and split into train and test sets.
    """
    from backend.app.services.preprocessing import PreprocessingService

    if not RAW_DATA_PATH.exists():
        RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df = generate_synthetic_dataset(n_samples=600, random_state=random_state)
        df.to_csv(RAW_DATA_PATH, index=False)

    df = pd.read_csv(RAW_DATA_PATH)
    X, y = PreprocessingService.prepare_dataset(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test
