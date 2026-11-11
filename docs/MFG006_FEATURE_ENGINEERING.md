# MFG006 Disruption Dataset: Feature Engineering Specification

This document details the design, mathematical formulation, domain rationale, and validation of the **4 engineered pre-disruption features** implemented in [`ml/mfg006_preprocessing.py`](file:///c:/Users/Lenovo/Desktop/EDI%20SEM%205%20PROJECT%20FILE/ml/mfg006_preprocessing.py) and applied uniformly across training and FastAPI inference.

---

## 1. Feature Engineering Principles & Zero-Leakage Guarantee

1. **Ex-Ante Temporal Availability**: Every single engineered feature is constructed strictly from operational parameters, contract baselines, and historical audit metrics that exist **prior to any physical disruption**.
2. **Defensive Numerical Safety**: All division operations incorporate lower-bound clamping (`clip(lower=1.0)`) to permanently prevent division-by-zero errors. Missing or corrupt inputs are handled gracefully with robust medians/defaults.
3. **Parity Between Training and Production**: The exact same `add_engineered_features()` function is executed in the offline training pipeline and in the online FastAPI prediction endpoint.

---

## 2. Detailed Specification of Engineered Features

### 2.1 Feature 1: `buffer_to_lead_time_ratio`

- **Conceptual Meaning**: Quantifies the facility's inventory decoupling capacity relative to the supplier's transit lead time. A ratio $> 1.0$ indicates that on-hand inventory buffer can fully absorb a supply cessation equal to the normal lead time. A ratio $< 0.25$ indicates dangerous inventory vulnerability.
- **Source Columns**:
  - `inventory_buffer_days_at_onset` (`float64`, Range: 0.0 to 90.0 days, Mean: 25.4 days)
  - `normal_lead_time_days` (`float64`, Range: 10.0 to 150.0 days, Mean: 58.2 days)
- **Pre-Disruption Availability**: Both values are contractual baselines established in ERP before disruption events.
- **Mathematical Formula**:
  $$\text{buffer\_to\_lead\_time\_ratio} = \frac{\text{inventory\_buffer\_days\_at\_onset}}{\max(1.0, \text{normal\_lead\_time\_days})}$$
- **Summary Statistics on MFG006**:
  - Minimum: `0.0085`
  - 25th Percentile: `0.1746`
  - Median (50%): `0.3371`
  - 75th Percentile: `0.6983`
  - Maximum: `11.9844`
  - Missing Values: `0`

---

### 2.2 Feature 2: `single_source_dependency_flag`

- **Conceptual Meaning**: Binary indicator flagging extreme single-point-of-failure exposure. Fired when a single vendor controls $70\%$ or more of procurement volume AND the enterprise has $0$ pre-qualified backup suppliers.
- **Source Columns**:
  - `supplier_concentration_pct` (`float64`, Range: 20.0% to 100.0%)
  - `number_of_alternative_suppliers` (`int64`, Range: 0 to 7)
- **Pre-Disruption Availability**: Determined directly from procurement directory and vendor spend reports.
- **Mathematical Formula**:
  $$\text{single\_source\_dependency\_flag} = \begin{cases} 1 & \text{if } \text{supplier\_concentration\_pct} \ge 70.0 \text{ and } \text{number\_of\_alternative\_suppliers} == 0 \\ 0 & \text{otherwise} \end{cases}$$
- **Summary Statistics on MFG006**:
  - Value `0` (Diversified / Lower Concentration): `2,544` cases (84.8%)
  - Value `1` (Critical Single-Source Exposure): `456` cases (15.2%)
  - Missing Values: `0`

---

### 2.3 Feature 3: `supplier_risk_index`

- **Conceptual Meaning**: Multi-factor composite index synthesizing external location fragility, internal financial solvency, and audited quality assurance into a unified 0 to 100 scale.
- **Source Columns**:
  - `supplier_geographic_risk_score` (`float64`, Range: 0.0 to 10.0, higher = riskier)
  - `supplier_financial_health_score` (`float64`, Range: 0.0 to 10.0, higher = healthier)
  - `supplier_audit_score_last` (`float64`, Range: 0.0 to 100.0, higher = better quality)
- **Pre-Disruption Availability**: Sourced from annual audits, credit monitoring (e.g. Dun & Bradstreet / Altman-Z), and geopolitical country risk indices.
- **Mathematical Formula**:
  $$\text{supplier\_risk\_index} = 4.0 \cdot S_{\text{geo}} + 3.5 \cdot (10.0 - S_{\text{fin}}) + 0.25 \cdot (100.0 - S_{\text{audit}})$$
  *(Bounded within $[0.0, 100.0]$).*
- **Summary Statistics on MFG006**:
  - Minimum: `9.38`
  - 25th Percentile: `29.68`
  - Median (50%): `36.94`
  - 75th Percentile: `44.38`
  - Maximum: `69.58`
  - Missing Values: `0`

---

### 2.4 Feature 4: `audit_governance_risk`

- **Conceptual Meaning**: Measures governance staleness. Time elapsed since the last audit represents a risk multiplier; if a vendor previously had a poor audit score, every additional un-audited month dramatically compounds operational uncertainty.
- **Source Columns**:
  - `months_since_last_audit` (`int64`, Range: 0 to 48 months)
  - `supplier_audit_score_last` (`float64`, Range: 0.0 to 100.0)
- **Pre-Disruption Availability**: Logged in vendor governance tracking databases.
- **Mathematical Formula**:
  $$\text{audit\_deficiency} = \frac{100.0 - \text{supplier\_audit\_score\_last}}{100.0}$$
  $$\text{audit\_governance\_risk} = \text{months\_since\_last\_audit} \times \text{audit\_deficiency}$$
- **Summary Statistics on MFG006**:
  - Minimum: `0.00` (recently audited with near-perfect score)
  - 25th Percentile: `1.96`
  - Median (50%): `4.74`
  - 75th Percentile: `8.50`
  - Maximum: `31.35`
  - Missing Values: `0`

---

## 3. Summary of Feature Dimensions

With these 4 engineered features added, the final input matrix $X$ expands from **40 raw features** to **44 model features**:
- **Numerical Features (24)**: 21 raw + 3 engineered (`buffer_to_lead_time_ratio`, `supplier_risk_index`, `audit_governance_risk`)
- **Categorical Features (12)**: 12 raw
- **Boolean Features (8)**: 7 raw + 1 engineered (`single_source_dependency_flag`)
- **After One-Hot Encoding**: Transformed feature vector contains **151 dense numerical columns**.
