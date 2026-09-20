"""
Model Evaluation and Comparison Script.
Computes real execution metrics: Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
"""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from ml.preprocessing import load_and_split_data
from backend.app.services.preprocessing import PreprocessingService

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def evaluate_models():
    X_train, X_test, y_train, y_test = load_and_split_data()

    rf_path = MODELS_DIR / "random_forest.pkl"
    xgb_path = MODELS_DIR / "xgboost.pkl"

    if not rf_path.exists() or not xgb_path.exists():
        raise FileNotFoundError("Models not trained yet. Run `python -m ml.train` first.")

    rf_model = joblib.load(rf_path)
    xgb_model = joblib.load(xgb_path)

    models = {
        "Random Forest": rf_model,
        "XGBoost": xgb_model
    }

    results = []
    target_names = [PreprocessingService.INV_LABEL_MAP[i] for i in sorted(PreprocessingService.INV_LABEL_MAP.keys())]

    print("\n" + "=" * 65)
    print("           REAL MODEL EVALUATION & COMPARISON METRICS")
    print("=" * 65)

    for name, model in models.items():
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1": f1
        })

        print(f"\n--- {name} ---")
        print(f"Accuracy  : {acc:.4f}")
        print(f"Precision : {prec:.4f}")
        print(f"Recall    : {rec:.4f}")
        print(f"F1-Score  : {f1:.4f}")
        print("\nConfusion Matrix:")
        print(pd.DataFrame(cm, index=[f"Actual_{t}" for t in target_names], columns=[f"Pred_{t}" for t in target_names]))
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

    summary_df = pd.DataFrame(results)
    print("\n" + "=" * 65)
    print("                       COMPARISON TABLE")
    print("=" * 65)
    print(summary_df.to_string(index=False))
    print("=" * 65 + "\n")

    return summary_df


if __name__ == "__main__":
    evaluate_models()
