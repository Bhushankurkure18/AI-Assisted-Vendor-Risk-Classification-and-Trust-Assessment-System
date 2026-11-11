# AI-Assisted Vendor Risk Classification and Trust Assessment System
## Comprehensive Project Methodology & Quantitative Scoring Framework

```
========================================================================================
PROJECT TITLE: AI-Assisted Vendor Risk Classification and Trust Assessment System
MODULE:        Structured ML Component & Multi-Tier Scoring Architecture
DATASET:       MFG006 Disruption Dataset (mfg006_disruptions.csv)
TARGET:        severity_level (LOW, MEDIUM, HIGH, CRITICAL)
DATE:          September 2026 / Academic Year 2026–2027
LOCATION:      docs/PROJECT_METHODOLOGY_AND_SCORING.md
========================================================================================
```

---

## 1. Executive Overview & System Architecture

### 1.1 Context and Problem Statement
Global supply chain disruptions—stemming from geopolitical instability, cyberattacks, single-source dependency, freight congestion, and supplier financial insolvency—pose substantial financial and operational hazards to modern manufacturing enterprises. Traditional vendor risk management relies on static annual questionnaires, lagged credit scores, and subjective reviews. These methods fail to quantify ex-ante disruption severity or dynamically adapt to operational indicators.

This project delivers an **AI-Assisted Vendor Risk Classification and Trust Assessment System**. The core purpose of the structured ML subsystem is to predict the **operational and financial severity level of potential disruptions** (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) using **only pre-disruption signals**, and translate those predictions into an actionable, multi-dimensional **Trust Assessment Score (TAS)**.

### 1.2 System Architecture Diagram

```
                                  PRE-DISRUPTION VENDOR & SUPPLY CHAIN INPUTS
                  (Supplier Profile, Inventory Buffer, Lead Times, Volatility, Early Warnings)
                                                       │
                                                       ▼
                       ┌───────────────────────────────────────────────────────────────┐
                       │                     FASTAPI GATEWAY / REST API                │
                       │           (Payload Validation, Schema Enforcement, Auth)      │
                       └───────────────────────────────┬───────────────────────────────┘
                                                       │
                                                       ▼
                       ┌───────────────────────────────────────────────────────────────┐
                       │             DATA INGESTION & ZERO-LEAKAGE PIPELINE            │
                       │  - Imputation (Median / Mode)  - One-Hot / Ordinal Encoding   │
                       │  - Robust Scaling              - Zero Post-Event Contamination│
                       └───────────────────────────────┬───────────────────────────────┘
                                                       │
                        ┌──────────────────────────────┼──────────────────────────────┐
                        │                              │                              │
                        ▼                              ▼                              ▼
        ┌──────────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
        │     TIER 1: DETERMINISTIC    │ │    TIER 2: RANDOM FOREST  │ │     TIER 3: XGBOOST       │
        │       RULE-BASED ENGINE      │ │   MULTICLASS CLASSIFIER   │ │   MULTICLASS CLASSIFIER   │
        │ - 5 Weighted Risk Dimensions │ │ - 100 Balanced Trees      │ │ - Gradient Boosted Trees  │
        │ - Transparent Risk Score     │ │ - Class-Weighted Loss     │ │ - Softmax Probabilities   │
        │ - Deterministic Fallback     │ │ - Tree-Based Importance   │ │ - Non-Linear Interactions │
        └──────────────┬───────────────┘ └─────────────┬─────────────┘ └─────────────┬─────────────┘
                       │                               │                             │
                       └───────────────────────────────┼─────────────────────────────┘
                                                       │
                                                       ▼
                       ┌───────────────────────────────────────────────────────────────┐
                       │               DECISION, TRUST & EXPLAINABILITY ENGINE         │
                       │  - Expected Severity Index (ESI) Calculation                  │
                       │  - Trust Assessment Score (TAS) Formulation                   │
                       │  - Feature Attribution & Top Risk Driver Extraction           │
                       └───────────────────────────────┬───────────────────────────────┘
                                                       │
                                                       ▼
                       ┌───────────────────────────────────────────────────────────────┐
                       │                   STRUCTURED RISK & TRUST DOSSIER             │
                       │  - Predicted Severity Level (Low / Medium / High / Critical)  │
                       │  - Class Probabilities: P(Low), P(Med), P(High), P(Crit)      │
                       │  - Quantitative Trust Score (0-100) & Trust Tier              │
                       │  - Actionable Mitigation Guidance for Procurement Officers    │
                       └───────────────────────────────────────────────────────────────┘
```

---

## 2. Zero-Target-Leakage Methodology

### 2.1 The Critical Temporal Boundary Principle
In predictive risk modeling, **target leakage** occurs when variables that could only be known *after* an event occurs are included as model inputs. If post-event variables are included:
1. Model accuracy is artificially inflated during training/validation (near 100% precision/recall).
2. The model becomes completely unusable in real-world deployment, because operational users do not have access to post-event statistics when evaluating an active vendor.

```
─────────────────────────────────────────────┬─────────────────────────────────────────────
              PRE-DISRUPTION                 │               POST-DISRUPTION
          (Available to Model)               │              (STRICTLY EXCLUDED)
─────────────────────────────────────────────┼─────────────────────────────────────────────
• Supplier Financial Health Score (1-10)     │ • Actual Revenue Loss (USD)
• Normal Contracted Lead Time (Days)         │ • Production Lines Halted / Throttled
• Inventory Buffer Days at Onset             │ • Stockout Occurrence & Duration (Days)
• Sourcing Concentration (%)                 │ • Realized Throughput Loss (%)
• Number of Alternative Suppliers (Count)    │ • Disruption Duration (Days)
• Primary Logistics Mode (Ocean/Air/Road)    │ • Expediting & Rush Freight Spend (USD)
• Safety Stock Policy Status                 │ • Recovery Trajectory (V/U/L Shaped)
• Early Warning Lead Time (Days)             │ • Time to 50% & Full Recovery (Days)
• Supply Chain Visibility Score (1-5)        │ • Post-Event Supplier Status (Exited/Retained)
• Pre-Event Resilience Posture               │ • Insurance Claim & Settlement Payout
─────────────────────────────────────────────┴─────────────────────────────────────────────
                     ▲                                             ▲
                     │                                             │
             VALID PREDICTORS                             CRITICAL LEAKAGE (DROPPED)
```

### 2.2 Empirical Audit of the MFG006 Dataset
The `mfg006_disruptions.csv` dataset contains 3,000 historical disruption records across 113 attributes. A rigorous semantic and correlation audit classified every single column:

1. **Target Variable (`1` column)**:
   - `severity_level`: Categorical ground-truth impact (`low`, `medium`, `high`, `critical`).
2. **Direct Target Proxy (`1` column — REMOVED)**:
   - `severity_score`: Continuous numerical score directly used to compute `severity_level` (correlation $> 0.95$). Including this would represent instantaneous 100% label leakage.
3. **Identifiers, Constants & Administrative Tags (`11` columns — REMOVED)**:
   - `event_id`, `company_id`, `plant_id`, `supplier_id`, `supplier_name_synthetic`: Arbitrary entity IDs with no generalizable predictive power.
   - `sku`: Zero-variance constant (`"MFG-006"` for 100% of rows).
   - `event_detection_date`, `event_start_date`, `event_resolution_date`, `inventory_depletion_date`: Timestamps.
   - `affected_country`: 100% collinear duplicate of `supplier_country`.
4. **Post-Disruption Leakage Variables (`60` columns — REMOVED)**:
   - Realized financial loss: `actual_revenue_loss_usd`, `ebitda_impact_usd`, `cost_of_disruption_total_usd`, `expediting_cost_usd`.
   - Realized plant impacts: `production_lines_halted`, `production_lines_throttled`, `throughput_loss_pct`, `stockout_occurred`, `stockout_duration_days`.
   - Realized transit delays: `lead_time_extension_pct`, `disrupted_lead_time_days`, `carrier_failure_flag`, `freight_cost_premium_usd`.
   - Reactive mitigation decisions: `spot_buy_activated`, `alternative_supplier_onboarded`, `mitigation_effectiveness_score`, `resilience_investment_usd`.
   - Post-event recovery & audit: `time_to_full_recovery_days`, `recovery_trajectory`, `post_event_supplier_status`, `lessons_learned_documented`, `insurance_payout_usd`.
5. **Approved Pre-Disruption Feature Set (`40` columns — KEPT)**:
   - Consists of **22 numerical metrics**, **11 categorical variables**, and **7 boolean indicators**, all available **prior to physical disruption onset**.
   - Contains **0 missing values** across all 3,000 records.

---

## 3. Data Preprocessing & Validation Pipeline

### 3.1 Leakage-Free Preprocessing Pipeline Architecture
To prevent train-to-test contamination, all transformations are encapsulated in an immutable scikit-learn `Pipeline` and `ColumnTransformer`. Transformers are **fit strictly on training data** and merely applied (via `.transform()`) to validation, test, and production payloads.

```python
preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", RobustScaler())  # Resilient to heavy financial / volume tails
            ]),
            NUMERICAL_PRE_DISRUPTION_FEATURES
        ),
        (
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ]),
            CATEGORICAL_PRE_DISRUPTION_FEATURES
        ),
        (
            "bool",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("passthrough", FunctionTransformer(lambda x: x.astype(int)))
            ]),
            BOOLEAN_PRE_DISRUPTION_FEATURES
        )
    ]
)
```

### 3.2 Stratified Partitioning & Class Imbalance Strategy
The target variable exhibits an operational real-world distribution:
- **`medium`**: 1,185 samples (39.50%)
- **`low`**: 1,163 samples (38.77%)
- **`high`**: 473 samples (15.77%)
- **`critical`**: 179 samples (5.97%)

#### Methodological Protections:
1. **Stratified Splitting**: An 80/20 train/test split with `stratify=y` and `random_state=42` ensures identical class ratios in both splits (e.g., exactly ~5.97% Critical cases in train and test).
2. **Loss Weighting**:
   - Random Forest utilizes `class_weight="balanced"`, which weights sample loss inversely proportional to class frequencies:
     $$w_c = \frac{N}{K \cdot N_c}$$
     where $N$ is total samples, $K$ is number of classes (4), and $N_c$ is count of class $c$.
   - XGBoost utilizes custom sample weights derived from the training set class distribution to penalize false negatives on `CRITICAL` and `HIGH` tiers.
3. **Macro-Averaged Metric Primary Benchmark**: Models are evaluated primarily on **Macro F1-Score** and **Per-Class Recall** rather than overall accuracy, preventing majority-class dominance.

---

## 4. Quantitative Scoring & Trust Assessment Framework

The system combines deterministic domain engineering with probabilistic machine learning to output two core metrics:
1. **Disruption Risk Severity Index (RSI)** (Higher = More Dangerous)
2. **Trust Assessment Score (TAS)** (Higher = More Trustworthy)

### 4.1 Dimension-Wise Risk Formulation (Pre-Disruption Operational Dimensions)
The pre-disruption features are organized into **5 Normalized Risk Dimensions** ($0 \le S_d \le 100$):

#### Dimension 1: Supplier Vulnerability & Financial Health ($S_{SV}$)
Measures the intrinsic structural stability of the vendor entity:
$$S_{SV} = 100 - \left[ 0.50 \cdot (\text{supplier\_financial\_health\_score} \times 10) + 0.30 \cdot \text{supplier\_audit\_score\_last} + 0.20 \cdot \min(100, \text{relationship\_years} \times 10) \right]$$
*A financially fragile vendor with poor audit scores generates high vulnerability ($S_{SV} \to 100$).*

#### Dimension 2: Sourcing Dependency & Concentration ($S_{DC}$)
Measures single-point-of-failure exposure:
$$S_{DC} = \left[ 0.60 \cdot \text{supplier\_concentration\_pct} \right] + \left[ 0.40 \cdot \max(0, 100 - (\text{num\_alternative\_suppliers} \times 20)) \right]$$
*If concentration is 100% and alternatives are 0, $S_{DC} = 100$. If dual sourcing exists (`dual_source_in_place == True`), $S_{DC}$ receives a 20% dampening credit.*

#### Dimension 3: Operational Lead Time & Inventory Buffer ($S_{OB}$)
Measures the facility's vulnerability to supply cessation:
$$\text{Buffer Ratio} = \frac{\text{inventory\_buffer\_days\_at\_onset}}{\max(1.0, \text{normal\_lead\_time\_days})}$$
$$S_{OB} = \max\left(0, \min\left(100, 100 \cdot (1.0 - \text{Buffer Ratio})\right)\right)$$
*If buffer days $\ge$ normal lead time (Buffer Ratio $\ge 1.0$), inventory can absorb lead time delay, so $S_{OB} \to 0$. If buffer is negligible relative to lead time, $S_{OB} \to 100$.*

#### Dimension 4: Geographic & Logistics Fragility ($S_{GL}$)
Measures transport mode and regional exposure:
$$S_{GL} = 0.50 \cdot (\text{supplier\_geographic\_risk\_score} \times 10) + 0.30 \cdot W_{\text{mode}} + 0.20 \cdot W_{\text{carrier}}$$
Where:
- $W_{\text{mode}}$: Ocean Freight = 75, Intermodal = 60, Rail = 50, Road = 40, Air Freight = 25.
- $W_{\text{carrier}}$: Single Carrier = 90, Dual Carrier = 50, Multi-Carrier = 25, Own Fleet = 10.
- If `nearshoring_available == True`, $S_{GL}$ is reduced by 15 points.

#### Dimension 5: Supply Chain Visibility & Governance Readiness ($S_{VG}$)
Measures organizational preparedness and early detection capacity:
$$S_{VG} = 100 - \left[ 0.40 \cdot (\text{visibility\_score} \times 20) + 0.30 \cdot (\text{maturity\_score} \times 20) + 0.30 \cdot W_{\text{early\_warn}} \right]$$
Where $W_{\text{early\_warn}} = 100$ if early warning was detected with lead days $> 14$, $50$ if lead days $1\text{–}14$, and $0$ if no warning detected.

---

### 4.2 Composite Rule-Based Disruption Risk Score ($R_{\text{comp}}$)
The deterministic baseline aggregates the 5 dimensions through an empirically calibrated weighting matrix:

$$R_{\text{comp}} = w_{SV} \cdot S_{SV} + w_{DC} \cdot S_{DC} + w_{OB} \cdot S_{OB} + w_{GL} \cdot S_{GL} + w_{VG} \cdot S_{VG}$$

| Risk Dimension | Symbol | Weight ($w_d$) | Rationale |
|---|---|---|---|
| **Supplier Vulnerability** | $S_{SV}$ | **25%** ($0.25$) | Fundamental credit and quality capacity |
| **Sourcing Dependency** | $S_{DC}$ | **25%** ($0.25$) | Single-point-of-failure severity multiplier |
| **Operational & Buffer Risk** | $S_{OB}$ | **20%** ($0.20$) | Decoupling ability during supply pause |
| **Geographic & Logistics Risk** | $S_{GL}$ | **15%** ($0.15$) | Transit fragility and transit duration |
| **Visibility & Governance Readiness** | $S_{VG}$ | **15%** ($0.15$) | Advanced detection and preparedness |
| **Total** | | **100%** ($1.00$) | Normalized 0 to 100 scale |

#### Deterministic Severity Classification Thresholds:
```
  0.0 ──────────────── 39.99 ─────────────── 69.99 ─────────────── 84.99 ────────────── 100.0
 [        LOW        ] [       MEDIUM      ] [        HIGH       ] [      CRITICAL     ]
```
- **`LOW` (0.00 – 39.99)**: Vendor operations stable; robust buffer; low geographic vulnerability.
- **`MEDIUM` (40.00 – 69.99)**: Moderate dependency or moderate buffer; disruption manageable without line halts.
- **`HIGH` (70.00 – 84.99)**: High concentration or vulnerable financial health; significant threat to production lines.
- **`CRITICAL` (85.00 – 100.0)**: Single-sourced critical component with negligible buffer and elevated financial/geo risk.

---

### 4.3 Machine Learning Expected Severity Index ($ESI$)
Both Random Forest and XGBoost output a calibrated softmax probability distribution across the 4 classes:
$$\mathbf{P} = [P(\text{Low}), P(\text{Medium}), P(\text{High}), P(\text{Critical})], \quad \sum_{c} P(c) = 1.0$$

The continuous **Expected Severity Index ($ESI$)** maps the discrete distribution onto a continuous severity gradient ($1.0 \le ESI \le 4.0$):
$$ESI = 1.0 \cdot P(\text{Low}) + 2.0 \cdot P(\text{Medium}) + 3.0 \cdot P(\text{High}) + 4.0 \cdot P(\text{Critical})$$

Normalized Severity Score ($R_{ML}$, scaled 0 to 100):
$$R_{ML} = \frac{ESI - 1.0}{3.0} \times 100$$

---

### 4.4 Trust Assessment Score ($TAS$) Formulation

#### Definition of Trust
In vendor relationship management, **Trust** is defined as the mathematical expectation that a vendor will reliably fulfill contractual obligations without catastrophic disruption, backed by transparent governance and predictable operating baselines.

#### Trust Mathematical Formula:
$$TAS = \max\left(0.0, \min\left(100.0, \; 100 \cdot (1 - \hat{R}) \times C_{\text{cert}} \times G_{\text{audit}}\right)\right)$$

Where:
1. **Blended Risk ($\hat{R}$)**:
   $$\hat{R} = 0.30 \cdot \left(\frac{R_{\text{comp}}}{100}\right) + 0.70 \cdot \left(\frac{R_{ML}}{100}\right)$$
   *(Harmonizes deterministic domain safeguards with non-linear machine learning patterns).*
2. **Prediction Certainty Factor ($C_{\text{cert}}$)**:
   Penalizes high entropy / ambiguous model predictions:
   $$C_{\text{cert}} = 1.0 - \frac{H(\mathbf{P})}{\log_2(4)} \times 0.20, \quad H(\mathbf{P}) = -\sum_{c=1}^{4} P(c) \log_2 P(c)$$
   *(When the model is 100% confident in a class, $H(\mathbf{P})=0 \implies C_{\text{cert}}=1.0$. If the model is completely uncertain ($P=0.25$ across all classes), $C_{\text{cert}}=0.80$).*
3. **Governance & Audit Recency Multiplier ($G_{\text{audit}}$)**:
   $$G_{\text{audit}} = \begin{cases}
   1.00 & \text{if } \text{months\_since\_last\_audit} \le 12 \\
   0.95 & \text{if } 12 < \text{months\_since\_last\_audit} \le 24 \\
   0.85 & \text{if } 24 < \text{months\_since\_last\_audit} \le 36 \\
   0.75 & \text{if } \text{months\_since\_last\_audit} > 36
   \end{cases}$$

#### Trust Tier Categorization Table:
| Trust Score ($TAS$) | Trust Tier | Classification Meaning | Operational Action in Procurement |
|---|---|---|---|
| **85.0 – 100.0** | **Tier 1: Strategic Partner** | Exceptional reliability, robust financial posture, verified audits | Preferred allocation; eligible for long-term sole-sourcing agreements |
| **70.0 – 84.9** | **Tier 2: Qualified / Standard** | Stable performance with standard risk parameters | Standard procurement terms; annual audit cycle |
| **50.0 – 69.9** | **Tier 3: Conditional / Guarded** | Elevated vulnerability, inventory buffer concerns, or aging audits | Dual-sourcing mandatory; monthly buffer tracking; spot-buy contingency |
| **0.0 – 49.9** | **Tier 4: Restricted / High Risk** | High probability of severe/critical disruption; unacceptable exposure | Supplier review board convened; freeze volume expansion; active exit strategy |

---

## 5. Multi-Model Architecture & Training Workflow

```
       DATA PREPARATION                       MODEL TRAINING                           EVALUATION
┌─────────────────────────────┐        ┌─────────────────────────────┐        ┌─────────────────────────────┐
│  MFG006 Disruption Dataset  │        │   Rule-Based Baseline       │        │ Multi-Metric Benchmarking   │
│  (3,000 Rows x 113 Cols)    │        │   (ml/rule_based_baseline)  │───────▶│ - Macro/Weighted Precision  │
└──────────────┬──────────────┘        └─────────────────────────────┘        │ - Macro/Weighted Recall     │
               │                                                              │ - Macro/Weighted F1-Score   │
               ▼                               ┌─────────────────────────────┐│ - 4x4 Confusion Matrix      │
┌─────────────────────────────┐                │   Random Forest Classifier  ││ - Adjacent Error Tracking   │
│ Feature Isolation & Split   │───────────────▶│   (models/mfg006_rf.joblib) │───────▶                     │
│ - 40 Pre-Disruption (X)     │                └─────────────────────────────┘└──────────────┬──────────────┘
│ - severity_level (y)        │                                                              │
│ - Stratified 80/20 Split    │                ┌─────────────────────────────┐               │
└──────────────┬──────────────┘                │   XGBoost Multiclass        │               │
               │                               │   (models/mfg006_xgb.joblib)│───────────────┘
               ▼                               └─────────────────────────────┘               │
┌─────────────────────────────┐                                                              ▼
│  Fitted ColumnTransformer   │──────────────────────────────────────────────────▶ ARTIFACT PERSISTENCE
│  (models/mfg006_prep.joblib)│                                                    - joblib model binaries
└─────────────────────────────┘                                                    - feature metadata JSON
                                                                                   - evaluation CSV reports
```

### 5.1 Model Specifications
1. **Rule-Based Baseline Classifier**:
   - Deterministic implementation of Section 4.2 composite score.
   - Evaluated on the held-out 20% test split to provide a benchmark for ML value-add.
2. **Random Forest Classifier**:
   - `n_estimators=200`, `max_depth=12`, `min_samples_split=5`, `class_weight='balanced'`, `random_state=42`.
   - Generates non-linear decision boundaries resilient to monotonic outliers.
3. **XGBoost Classifier**:
   - `objective='multi:softprob'`, `num_class=4`, `n_estimators=200`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `random_state=42`.
   - Employs gradient-based tree boosting with regularized shrinkage ($\gamma, \lambda$).

---

## 6. Explainability & Risk Driver Attribution

Modern procurement compliance requires that machine learning models provide **interpretable explanations** for every decision. Black-box scores are legally and operationally unviable for supply chain decisions.

### 6.1 Global Feature Importance
1. **Gini / Mean Decrease in Impurity (MDI)**: Quantifies total variance reduction across all trees for each pre-disruption variable.
2. **Permutation Importance**: Shuffles feature values in the test set to measure the degradation in Macro F1 score, avoiding cardinality bias.

### 6.2 Local Prediction Attribution (Per-Vendor Explanation)
When predicting risk for an individual vendor, the system extracts the **top 3 risk drivers** and **top 2 resilience mitigators**:
- **Risk Driver Example**: `"High Sourcing Concentration (85.0%) with 0 alternative suppliers amplifies single-point-of-failure risk."`
- **Mitigating Factor Example**: `"Dual Sourcing actively contracted and 45.0 days of buffer inventory dampens potential disruption severity."`

---

## 7. FastAPI Integration & API Specification

The FastAPI backend exposes the trained ML and scoring pipeline via clean, typed REST endpoints without modifying or breaking existing vendor database services:

### 7.1 Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/ml/health` | Verifies trained model binaries and preprocessor are loaded in memory |
| `POST` | `/api/v1/ml/predict` | Computes predicted severity level, class probabilities, and ESI |
| `POST` | `/api/v1/ml/assess` | Full pipeline: computes composite risk, ML prediction, and Trust Assessment Score (TAS) |
| `POST` | `/api/v1/ml/risk-explanation` | Returns local feature attributions and primary risk drivers for a vendor profile |

### 7.2 Sample Assessment Request Payload (`POST /api/v1/ml/assess`)
```json
{
  "supplier_tier": 1,
  "supplier_criticality": "strategic_partner",
  "supplier_country": "JP",
  "supplier_geographic_risk_score": 2.96,
  "number_of_alternative_suppliers": 0,
  "supplier_concentration_pct": 80.1,
  "affected_component_category": "electronic_component",
  "supplier_financial_health_score": 7.19,
  "supplier_audit_score_last": 57.6,
  "months_since_last_audit": 17,
  "supplier_relationship_years": 7.9,
  "dual_source_in_place": false,
  "affected_sku_count": 74,
  "industry_sector": "electronics",
  "affected_region": "Northeast_Asia",
  "supply_volume_at_risk_units": 883284,
  "revenue_at_risk_usd": 15505951.0,
  "inventory_buffer_days_at_onset": 12.6,
  "normal_lead_time_days": 85.6,
  "logistics_mode_primary": "ocean_freight",
  "freight_cost_normal_usd": 15771.0,
  "logistics_concentration_risk": "single_carrier",
  "nearshoring_available": false,
  "demand_volatility_index": 16.7,
  "demand_forecast_error_mape": 57.0,
  "order_variability_bullwhip_ratio": 4.03,
  "customer_concentration_top3_pct": 21.2,
  "safety_stock_adequacy": "insufficient",
  "disruption_category": "supplier_failure",
  "disruption_subcategory": "quality_failure",
  "early_warning_signal_detected": false,
  "early_warning_source": "none",
  "early_warning_lead_days": 0,
  "supply_chain_visibility_score": 3.62,
  "digital_twin_available": false,
  "erp_alert_triggered": false,
  "external_data_feed_active": false,
  "tier2_visibility_flag": false,
  "supply_chain_maturity_score": 2.4,
  "resilience_posture_pre_event": "compliant"
}
```

### 7.3 Sample Assessment Response Payload
```json
{
  "predicted_severity_level": "HIGH",
  "model_used": "XGBoost Classifier v1.0",
  "class_probabilities": {
    "low": 0.082,
    "medium": 0.245,
    "high": 0.583,
    "critical": 0.090
  },
  "expected_severity_index": 2.68,
  "normalized_ml_risk_score": 56.0,
  "rule_based_risk_score": 68.4,
  "trust_assessment_score": 42.6,
  "trust_tier": "Tier 4: Restricted / High Risk",
  "key_risk_drivers": [
    "Single-source dependency: supplier concentration is 80.1% with 0 qualified backup suppliers.",
    "Inventory buffer deficit: buffer of 12.6 days provides only 14.7% coverage against 85.6 normal lead time days.",
    "Ocean freight coupled with single-carrier logistics concentration."
  ],
  "mitigation_recommendations": [
    "Mandate dual-sourcing activation for affected electronic component SKUs.",
    "Increase inventory buffer from 12.6 days to minimum 45.0 days.",
    "Execute comprehensive supplier audit (current audit age: 17 months)."
  ]
}
```

---

## 8. Verification Protocol & Evaluation Standards

### 8.1 Metric Suite
Performance is documented across multiple axes on the 20% stratified test set ($N_{\text{test}} = 600$):
1. **Accuracy**: Baseline sanity metric.
2. **Macro Precision, Recall, and F1**: Unweighted arithmetic mean across classes; primary benchmark metric preventing bias toward `medium` and `low`.
3. **Weighted F1**: Overall performance taking class proportions into account.
4. **Per-Class Metrics**: Specific tracking of `CRITICAL` recall (target $\ge 75\%$) to minimize catastrophic unpredicted failures.
5. **Confusion Matrix Analysis**: Tracking adjacent mistakes:
   - Acceptable: `Medium` $\leftrightarrow$ `High`
   - Unacceptable / Heavy Penalty: `Low` $\leftrightarrow$ `Critical`

### 8.2 Automated Test Suite Structure
The test suite in `tests/test_mfg006_ml.py` verifies:
- Pipeline preprocessing on unseen data (no NaN output).
- Deterministic behavior of the rule-based risk calculation.
- Inference consistency between scikit-learn models and saved `.joblib` binaries.
- FastAPI endpoint responses and HTTP status codes (`200 OK`, `422 Unprocessable Entity` for invalid payloads).

---

## 9. Academic & Technical Governance

1. **Zero Fabrication**: All reported metrics, confusion matrices, and feature importance tables reflect actual script execution outputs on `mfg006_disruptions.csv`.
2. **Modular Architecture**: Model artifacts, feature metadata, and preprocessor pipelines are saved independently to ensure compatibility with future Phase 2 Multi-Agent / RAG modules.
3. **Transparent Assumptions**: Rule thresholds and dimension weights are explicitly documented as implementation choices grounded in procurement best practices.
