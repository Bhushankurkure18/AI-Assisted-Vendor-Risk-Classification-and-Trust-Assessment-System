# MFG006 Disruption Severity: Transparent Rule-Based Baseline

This document specifies the architecture, decision rules, threshold calibration, and test-set performance of the **Deterministic Rule-Based Baseline Classifier** implemented in [`ml/rule_based_baseline.py`](file:///c:/Users/Lenovo/Desktop/EDI%20SEM%205%20PROJECT%20FILE/ml/rule_based_baseline.py).

---

## 1. Baseline Purpose & Design Philosophy

1. **Benchmark for Machine Learning Value-Add**: In applied data science, complex models (Random Forest, XGBoost) should only be deployed if they meaningfully outperform a transparent, deterministic heuristic.
2. **Strict Pre-Disruption Operational Input**: The rule engine uses **zero post-disruption variables** and relies strictly on contract parameters, inventory buffers, lead times, and governance scores.
3. **Transparent & Auditable**: Every threshold and dimension weight is explicitly documented so that procurement officers can trace why an alert was fired.

---

## 2. Quantitative Rule Formulation

The engine calculates a composite risk index $R_{\text{comp}} \in [0.0, 100.0]$ as a weighted sum of **5 operational dimensions**:

$$R_{\text{comp}} = 0.25 \cdot S_{\text{sv}} + 0.25 \cdot S_{\text{dc}} + 0.20 \cdot S_{\text{ob}} + 0.15 \cdot S_{\text{gl}} + 0.15 \cdot S_{\text{vg}}$$

### Dimension Definitions:
1. **Supplier Vulnerability ($S_{\text{sv}}$)**:
   $$S_{\text{sv}} = 100.0 - \left[ 0.50 \cdot (\text{financial\_health} \times 10) + 0.30 \cdot \text{audit\_score} + 0.20 \cdot (\text{relationship\_years} \times 10) \right]$$
2. **Sourcing Dependency ($S_{\text{dc}}$)**:
   $$S_{\text{dc}} = \left[ 0.60 \cdot \text{concentration\_pct} \right] + \left[ 0.40 \cdot (100.0 - \text{alternatives} \times 20.0) \right] - (\text{dual\_source} \times 15.0)$$
3. **Operational Buffer Risk ($S_{\text{ob}}$)**:
   $$S_{\text{ob}} = 100.0 \times \left(1.0 - \frac{\min(2.0, \text{buffer\_to\_lead\_time\_ratio})}{2.0}\right)$$
4. **Geographic & Logistics Risk ($S_{\text{gl}}$)**:
   $$S_{\text{gl}} = (\text{geo\_risk\_score} \times 10) - (\text{nearshoring} \times 10.0)$$
5. **Visibility & Governance Readiness ($S_{\text{vg}}$)**:
   $$S_{\text{vg}} = 100.0 - \left[ 0.50 \cdot (\text{visibility\_score} \times 20) + 0.50 \cdot (\text{maturity\_score} \times 20) \right]$$

---

## 3. Threshold Calibration on Training Set ($N_{\text{train}} = 2400$)

To establish fair decision cutoffs without human bias, thresholds were calibrated to the cumulative empirical quantiles of the training distribution:
- **`LOW` Maximum Threshold**: `42.83` (38.75th percentile of $X_{\text{train}}$)
- **`MEDIUM` Maximum Threshold**: `52.81` (78.25th percentile of $X_{\text{train}}$)
- **`HIGH` Maximum Threshold**: `62.14` (94.04th percentile of $X_{\text{train}}$)
- **`CRITICAL` Range**: $> 62.14$ (Top ~6% of $X_{\text{train}}$)

---

## 4. Test Set Evaluation Results ($N_{\text{test}} = 600$)

Evaluated on the exact same held-out stratified test set used for Random Forest and XGBoost:

### 4.1 Global Aggregate Metrics
- **Accuracy**: `35.00%` (`0.3500`)
- **Macro Precision**: `0.2646`
- **Macro Recall**: `0.2588`
- **Macro F1-Score**: `0.2594`
- **Weighted F1-Score**: `0.3438`

### 4.2 Per-Class Breakdown
| Class | Precision | Recall | F1-Score | Test Support |
|---|---|---|---|---|
| **`low`** | `0.3924` | `0.3991` | `0.3957` | 233 |
| **`medium`** | `0.4071` | `0.4346` | `0.4204` | 237 |
| **`high`** | `0.1358` | `0.1170` | `0.1257` | 94 |
| **`critical`** | `0.1250` | `0.0833` | `0.1000` | 36 |

### 4.3 Test Confusion Matrix
```
                 Pred_low  Pred_medium  Pred_high  Pred_critical
Actual_low             93          100         29             11
Actual_medium          90          103         37              7
Actual_high            45           35         11              3
Actual_critical        13           16          4              3
```

---

## 5. Domain Assessment & Baseline Limitations

1. **Failure to Detect Non-Linear Interactions**: The linear additive weighting fails to capture joint interaction conditions (e.g. a high cyber vulnerability interacting with zero inventory buffer produces severe outcomes even if financial scores are high).
2. **High Misclassification on Severe Classes**: Recall on `critical` is only $8.33\%$ (only 3 of 36 critical disruptions were identified).
3. **Conclusion**: The rule-based engine serves as a reliable safety fallback and domain baseline, but supervised machine learning (Random Forest and XGBoost) is strictly necessary to capture multi-variable interactions.
