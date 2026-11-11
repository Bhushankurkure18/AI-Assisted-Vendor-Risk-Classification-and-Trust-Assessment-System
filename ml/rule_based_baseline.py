"""
Transparent Rule-Based Baseline Classifier for MFG006 Disruption Severity.

Implements a deterministic multi-factor risk scoring engine using only verified
pre-disruption operational variables across 5 dimensions:
1. Supplier Vulnerability (S_sv)
2. Sourcing Dependency (S_dc)
3. Operational Buffer & Lead Time Risk (S_ob)
4. Geographic & Logistics Risk (S_gl)
5. Visibility & Governance Readiness (S_vg)

Calibrates severity thresholds on the training set and evaluates strictly on the test set.
Outputs: 'low', 'medium', 'high', 'critical'.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from ml.mfg006_preprocessing import (
    load_and_split_mfg006_data,
    TARGET_CLASSES,
    LABEL_MAP,
    INV_LABEL_MAP
)

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"


class RuleBasedBaselineClassifier:
    """
    Deterministic domain rule engine for disruption severity prediction.
    """
    def __init__(
        self,
        threshold_low: float = 42.83,
        threshold_med: float = 52.81,
        threshold_high: float = 62.14
    ):
        # Implementation / prototype thresholds calibrated on training quantiles
        self.threshold_low = threshold_low
        self.threshold_med = threshold_med
        self.threshold_high = threshold_high

    @staticmethod
    def compute_dimension_scores(df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Compute the 5 normalized dimension risk scores (0 to 100).
        """
        # 1. Supplier vulnerability (0-100): Financial health, audit score, relationship
        fin_h = pd.to_numeric(df["supplier_financial_health_score"], errors="coerce").fillna(5.0).clip(0.0, 10.0)
        audit = pd.to_numeric(df["supplier_audit_score_last"], errors="coerce").fillna(50.0).clip(0.0, 100.0)
        rel_y = pd.to_numeric(df["supplier_relationship_years"], errors="coerce").fillna(3.0).clip(0.0, 10.0)
        s_sv = 100.0 - (0.50 * (fin_h * 10.0) + 0.30 * audit + 0.20 * (rel_y * 10.0))

        # 2. Sourcing dependency (0-100): Concentration, alternatives, dual sourcing
        conc = pd.to_numeric(df["supplier_concentration_pct"], errors="coerce").fillna(50.0).clip(0.0, 100.0)
        alts = pd.to_numeric(df["number_of_alternative_suppliers"], errors="coerce").fillna(1).clip(0, 5)
        dual = df["dual_source_in_place"].astype(int)
        s_dc = (0.60 * conc) + (0.40 * (100.0 - alts * 20.0)) - (dual * 15.0)

        # 3. Operational buffer & lead time (0-100): buffer relative to lead time
        if "buffer_to_lead_time_ratio" in df.columns:
            buffer_ratio = df["buffer_to_lead_time_ratio"]
        else:
            lead = pd.to_numeric(df["normal_lead_time_days"], errors="coerce").fillna(30.0).clip(lower=1.0)
            buf = pd.to_numeric(df["inventory_buffer_days_at_onset"], errors="coerce").fillna(0.0).clip(lower=0.0)
            buffer_ratio = buf / lead
        s_ob = 100.0 * (1.0 - (buffer_ratio.clip(0.0, 2.0) / 2.0))

        # 4. Geographic & logistics (0-100): Geo risk score, nearshoring
        geo_risk = pd.to_numeric(df["supplier_geographic_risk_score"], errors="coerce").fillna(5.0).clip(0.0, 10.0) * 10.0
        near = df["nearshoring_available"].astype(int)
        s_gl = geo_risk - (near * 10.0)

        # 5. Visibility and governance (0-100): Visibility score, maturity score
        vis = pd.to_numeric(df["supply_chain_visibility_score"], errors="coerce").fillna(3.0).clip(0.0, 5.0) * 20.0
        mat = pd.to_numeric(df["supply_chain_maturity_score"], errors="coerce").fillna(3.0).clip(0.0, 5.0) * 20.0
        s_vg = 100.0 - (0.50 * vis + 0.50 * mat)

        return {
            "supplier_vulnerability": s_sv.clip(0.0, 100.0),
            "sourcing_dependency": s_dc.clip(0.0, 100.0),
            "operational_buffer": s_ob.clip(0.0, 100.0),
            "geographic_logistics": s_gl.clip(0.0, 100.0),
            "visibility_governance": s_vg.clip(0.0, 100.0)
        }

    def compute_composite_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate weighted composite risk score (0 to 100).
        """
        dims = self.compute_dimension_scores(df)
        composite = (
            0.25 * dims["supplier_vulnerability"] +
            0.25 * dims["sourcing_dependency"] +
            0.20 * dims["operational_buffer"] +
            0.15 * dims["geographic_logistics"] +
            0.15 * dims["visibility_governance"]
        )
        return composite.clip(0.0, 100.0).round(2)

    def fit(self, X_train: pd.DataFrame, y_train: Optional[pd.Series] = None):
        """
        Calibrate quantile thresholds on the training set.
        """
        scores = self.compute_composite_score(X_train)
        self.threshold_low = float(np.percentile(scores, 38.75))
        self.threshold_med = float(np.percentile(scores, 78.25))
        self.threshold_high = float(np.percentile(scores, 94.04))
        return self

    def predict_indices(self, X: pd.DataFrame) -> np.ndarray:
        """
        Return numerical class indices (0=low, 1=medium, 2=high, 3=critical).
        """
        scores = self.compute_composite_score(X).values
        preds = np.zeros(len(scores), dtype=int)
        preds[(scores > self.threshold_low) & (scores <= self.threshold_med)] = 1
        preds[(scores > self.threshold_med) & (scores <= self.threshold_high)] = 2
        preds[scores > self.threshold_high] = 3
        return preds

    def predict(self, X: pd.DataFrame) -> List[str]:
        """
        Return string severity labels ('low', 'medium', 'high', 'critical').
        """
        preds = self.predict_indices(X)
        return [INV_LABEL_MAP[i] for i in preds]

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """
        Evaluate baseline performance on held-out test data.
        """
        y_pred = self.predict_indices(X_test)
        y_true = y_test.values

        acc = float(accuracy_score(y_true, y_pred))
        prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
        rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
        f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

        prec_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        rec_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
        f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        cm = confusion_matrix(y_true, y_pred).tolist()
        report_str = classification_report(y_true, y_pred, target_names=TARGET_CLASSES, zero_division=0)
        report_dict = classification_report(y_true, y_pred, target_names=TARGET_CLASSES, zero_division=0, output_dict=True)

        return {
            "model": "Rule-Based Baseline",
            "thresholds": {
                "low_max": round(self.threshold_low, 2),
                "medium_max": round(self.threshold_med, 2),
                "high_max": round(self.threshold_high, 2)
            },
            "accuracy": round(acc, 4),
            "macro_precision": round(prec_macro, 4),
            "macro_recall": round(rec_macro, 4),
            "macro_f1": round(f1_macro, 4),
            "weighted_precision": round(prec_weighted, 4),
            "weighted_recall": round(rec_weighted, 4),
            "weighted_f1": round(f1_weighted, 4),
            "confusion_matrix": cm,
            "classification_report_str": report_str,
            "per_class": {
                cls: {
                    "precision": round(report_dict[cls]["precision"], 4),
                    "recall": round(report_dict[cls]["recall"], 4),
                    "f1": round(report_dict[cls]["f1-score"], 4),
                    "support": report_dict[cls]["support"]
                }
                for cls in TARGET_CLASSES
            }
        }


def run_and_save_rule_baseline():
    """
    Fit baseline on X_train, evaluate on X_test, and save results.
    """
    X_train, X_test, y_train, y_test = load_and_split_mfg006_data(test_size=0.20, random_state=42)
    baseline = RuleBasedBaselineClassifier()
    baseline.fit(X_train, y_train)

    metrics = baseline.evaluate(X_test, y_test)
    print("=" * 65)
    print("RULE-BASED BASELINE EVALUATION (TEST SET)")
    print("=" * 65)
    print(f"Accuracy         : {metrics['accuracy']}")
    print(f"Macro F1-Score   : {metrics['macro_f1']}")
    print(f"Weighted F1-Score: {metrics['weighted_f1']}")
    print("\nClassification Report:")
    print(metrics["classification_report_str"])
    print("Confusion Matrix:")
    print(pd.DataFrame(
        metrics["confusion_matrix"],
        index=[f"Actual_{c}" for c in TARGET_CLASSES],
        columns=[f"Pred_{c}" for c in TARGET_CLASSES]
    ))
    return baseline, metrics


if __name__ == "__main__":
    run_and_save_rule_baseline()
