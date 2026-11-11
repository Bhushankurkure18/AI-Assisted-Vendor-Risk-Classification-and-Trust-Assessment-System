# MFG006 Disruption Dataset: Exploratory Data Analysis (EDA) Summary

This document synthesizes the empirical findings from the exploratory analysis of the **MFG006 Disruption Dataset** (`mfg006_disruptions.csv`). All 11 figures were generated programmatically and are saved in [`reports/figures/mfg006/`](file:///c:/Users/Lenovo/Desktop/EDI%20SEM%205%20PROJECT%20FILE/reports/figures/mfg006/).

---

## 1. Target Class Distribution (`severity_level`)
- **Figure Reference**: `01_target_class_distribution.png`
- **Class Proportions**:
  - `low`: 1,163 events (38.8%)
  - `medium`: 1,185 events (39.5%)
  - `high`: 473 events (15.8%)
  - `critical`: 179 events (6.0%)
- **Findings**:
  - The dataset displays realistic operational class imbalance. The majority of disruptions (78.3%) are low-to-medium friction events that are either absorbed by buffer stocks or mitigated with minor rescheduling.
  - Severe disruptions (`high` + `critical`) constitute 21.7% of all cases, with catastrophic events (`critical`) representing the narrow tail (6.0%).
  - **Modeling Implication**: Stratified train/test splitting (`stratify=y`) and class-weighted loss functions (`class_weight='balanced'` in Random Forest and tuned weighting in XGBoost) are required so the minority catastrophic failure mode is not suppressed by accuracy-driven optimization.

---

## 2. Key Numerical Feature Distributions
- **Figure Reference**: `02_numerical_feature_distributions.png`
- **Observations**:
  - `supplier_financial_health_score`: Spans 0.0 to 10.0 with a mean of 5.5 and a near-normal distribution.
  - `supplier_geographic_risk_score`: Spans 0.5 to 9.5 with a mean of 4.8.
  - `supplier_concentration_pct`: Concentrated between 40% and 85%, reflecting significant supplier reliance across manufacturing contracts.
  - `inventory_buffer_days_at_onset`: Right-skewed distribution ranging from 0 days to 90 days, with median ~25 days.
  - `normal_lead_time_days`: Mean ~60 days, ranging from 10 to 150 days.
  - `revenue_at_risk_usd`: Strongly right-skewed log-normal distribution, with values spanning from under $100K to over $25M.

---

## 3. Supplier Risk Characteristics Across Severity Levels
- **Figure References**: `03_financial_health_by_severity.png`, `04_geographic_risk_by_severity.png`, `06_alternative_suppliers_by_severity.png`, `07_audit_score_by_severity.png`, `08_supplier_concentration_by_severity.png`
- **Empirical Relationships**:
  - **Financial Health**: Lower financial health scores are more prevalent in higher severity disruptions. Suppliers facing liquidity crunches lack the buffer capital to expedite emergency parts or absorb operational shocks.
  - **Geographic Risk**: Critical disruptions display higher average geographic risk scores (regions with geopolitical instability or port gridlock).
  - **Alternative Suppliers**: Events with 0 or 1 qualified alternative supplier exhibit higher proportions of High and Critical outcomes. Dual-sourced components provide a dampening effect on severity.
  - **Supplier Concentration**: Disruption severity increases with higher single-supplier procurement concentration ($\ge 70\%$).
  - **Audit Scores & Recency**: Lower audit scores combined with greater time since last audit correlate with delayed risk mitigation and higher severity impact.

---

## 4. Supplier Criticality & Disruption Category Analysis
- **Figure References**: `05_supplier_criticality_by_severity.png`, `10_disruption_category_by_severity.png`
- **Observations**:
  - `strategic_partner` and `sole_source` classifications show elevated critical severity rates compared to `preferred` or `approved` vendors with fungible part substitutes.
  - **Disruption Categories**:
    - `supplier_failure` (financial insolvency, plant fires, quality recalls) generates the highest percentage of Critical and High severity disruptions (9.4% critical rate).
    - `cyber_attack` shows elevated High-severity rates (22.3%) due to abrupt digital shutdowns.
    - `logistics_delay` and `port_congestion` cluster primarily around Medium and Low severity, as inventory buffers frequently absorb moderate transit slippage.

---

## 5. Correlation Structure Among Numerical Predictors
- **Figure Reference**: `09_numerical_correlation_heatmap.png`
- **Findings**:
  - No pairs of pre-disruption numerical features exhibit critical collinearity ($|r| < 0.35$ for all raw feature pairs).
  - Features provide complementary, orthogonal operational signals across distinct domains: financial stability, geographic location, operational lead time, and supply chain governance.
  - This low inter-feature collinearity ensures numerical stability for both tree-based ensembles and distance-based scalers.

---

## 6. Outlier Analysis & Scaling Justification
- **Figure Reference**: `11_outlier_analysis_boxplots.png`
- **Findings**:
  - Financial values (`revenue_at_risk_usd`, `freight_cost_normal_usd`) and inventory buffer days exhibit substantial upper-tail outliers ($> 3$ IQR deviations from median).
  - Standard scaling ($\mu = 0, \sigma = 1$) would be disproportionately influenced by these extreme financial tails, compressing standard operating values into a narrow band.
  - **Justification for `RobustScaler`**: The preprocessing pipeline uses `RobustScaler` (scaling by median and Interquartile Range, $IQR = Q_{75} - Q_{25}$), which preserves variance structure without being distorted by multi-million-dollar revenue spikes.
