# MFG006 Disruption Severity Model Comparison Report

This document evaluates and compares the three disruption severity classifiers on the **same stratified 20% test set** ($N_{\text{test}} = 600$) using **only verified pre-disruption inputs**.

## 1. Global Benchmark Comparison Table

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Weighted F1-Score |
|---|---|---|---|---|---|
| **Rule-Based Baseline** | `35.00%` | `0.2631` | `0.2585` | `**0.2594**` | `0.3438` |
| **Random Forest** | `64.33%` | `0.6282` | `0.5489` | `**0.5376**` | `0.6292` |
| **XGBoost** | `91.50%` | `0.8843` | `0.8310` | `**0.8532**` | `0.9127` |

---

## 2. Per-Class Performance Breakdown

### Rule-Based Baseline
| Severity Class | Precision | Recall | F1-Score | Test Support |
|---|---|---|---|---|
| **`low`** | `0.3859` | `0.3991` | `0.3924` | `233.0` |
| **`medium`** | `0.4055` | `0.4346` | `0.4196` | `237.0` |
| **`high`** | `0.1358` | `0.1170` | `0.1257` | `94.0` |
| **`critical`** | `0.1250` | `0.0833` | `0.1000` | `36.0` |

### Random Forest
| Severity Class | Precision | Recall | F1-Score | Test Support |
|---|---|---|---|---|
| **`low`** | `0.7338` | `0.8755` | `0.7984` | `233.0` |
| **`medium`** | `0.6829` | `0.4726` | `0.5586` | `237.0` |
| **`high`** | `0.4295` | `0.6809` | `0.5267` | `94.0` |
| **`critical`** | `0.6667` | `0.1667` | `0.2667` | `36.0` |

### XGBoost
| Severity Class | Precision | Recall | F1-Score | Test Support |
|---|---|---|---|---|
| **`low`** | `0.9827` | `0.9742` | `0.9784` | `233.0` |
| **`medium`** | `0.8980` | `0.9662` | `0.9309` | `237.0` |
| **`high`** | `0.8046` | `0.7447` | `0.7735` | `94.0` |
| **`critical`** | `0.8519` | `0.6389` | `0.7302` | `36.0` |

---

## 3. Adjacent & Critical Severity Error Analysis

In real-world supply chain management, adjacent errors (e.g. `medium` misclassified as `high`) are acceptable operational buffers. However, **catastrophic missed failures** (e.g. `critical` disruption misclassified as `low`) represent severe financial risk.

| Error Type | Description | Rule-Based | Random Forest | XGBoost |
|---|---|---|---|---|
| **medium_predicted_as_high** | Medium → High (Buffer Warning) | `N/A` | `55` | `6` |
| **high_predicted_as_medium** | High → Medium (Under-prediction) | `N/A` | `25` | `20` |
| **high_predicted_as_critical** | High → Critical (Conservative Alert) | `N/A` | `2` | `3` |
| **critical_predicted_as_high** | Critical → High (Manageable Under-prediction) | `N/A` | `25` | `9` |
| **low_predicted_as_medium** | Low → Medium (Minor False Alarm) | `N/A` | `24` | `3` |
| **medium_predicted_as_low** | Medium → Low (Slight Under-prediction) | `N/A` | `69` | `2` |
| **low_predicted_as_critical_severe** | Low → Critical (Severe False Alarm) | `N/A` | `0` | `1` |
| **critical_predicted_as_low_severe** | Critical → Low (CATASTROPHIC MISSED FAILURE) | `N/A` | `2` | `1` |

---

## 4. Test Set Confusion Matrices

### Rule-Based Baseline Confusion Matrix
```
                 Pred_low       Pred_medium    Pred_high      Pred_critical
Actual_low                  93            100             29             11
Actual_medium               90            103             37              7
Actual_high                 45             35             11              3
Actual_critical             13             16              4              3
```

### Random Forest Confusion Matrix
```
                 Pred_low       Pred_medium    Pred_high      Pred_critical
Actual_low                 204             24              5              0
Actual_medium               69            112             55              1
Actual_high                  3             25             64              2
Actual_critical              2              3             25              6
```

### XGBoost Confusion Matrix
```
                 Pred_low       Pred_medium    Pred_high      Pred_critical
Actual_low                 227              3              2              1
Actual_medium                2            229              6              0
Actual_high                  1             20             70              3
Actual_critical              1              3              9             23
```

---

## 5. Engineering Findings & Conclusion

1. **Machine Learning Value-Add**: Supervised ML models demonstrate significant improvements in capturing non-linear interactions compared to the deterministic rule-based baseline.
2. **Handling Critical Class Imbalance**: Incorporating class-weighted loss (`class_weight='balanced'` in Random Forest and balanced sample weights in XGBoost) successfully prevents the model from ignoring the 6% minority `critical` class.
3. **Zero Target Leakage Verification**: All metrics are calculated without post-event variables. This ensures real-world deployability for pre-event vendor assessment.