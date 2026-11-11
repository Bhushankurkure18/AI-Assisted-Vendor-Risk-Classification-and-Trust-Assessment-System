# MFG006 Disruption Dataset: Feature Selection & Target Leakage Analysis

## Executive Summary

This document establishes the rigorous feature selection framework for migrating the **AI-Assisted Vendor Risk Classification and Trust Assessment System** from synthetic prototypes to the empirical **MFG006 Disruption Dataset** (`mfg006_disruptions.csv`).

The primary operational constraint is **Zero Target Leakage**: the predictive model must determine disruption/risk severity using **ONLY information that would be available BEFORE the disruption event occurs**.
Post-disruption variables (such as actual revenue loss, line halts, stockout duration, recovery time, expediting cost, and post-event supplier status) reflect consequences and reactive interventions; using them as model inputs would represent a catastrophic methodological failure.

### Dataset Geometry & Integrity Overview
- **Total Samples (Rows)**: `3000`
- **Total Attributes (Columns)**: `113`
- **Duplicate Records**: `0`
- **Target Variable**: `severity_level` (Multiclass: Low, Medium, High, Critical)
- **Target Proxy Excluded**: `severity_score` (Continuous direct derivative of target)
- **Candidate Pre-Disruption Features (KEPT)**: `40`
- **Post-Disruption & Leakage Features (REMOVED)**: `61`
- **Identifiers, Constants & Redundant Features (REMOVED)**: `11`

---
## 1. Target Variable (`severity_level`)

The prediction target is `severity_level`. It represents the overall operational and financial severity of a vendor/supply-chain disruption.

| Severity Level | Sample Count | Class Proportion | Description |
|---|---|---|---|
| **LOW** | `1163` | `38.77%` | Minor operational friction; minimal financial impact, absorbed by buffer stocks. |
| **MEDIUM** | `1185` | `39.5%` | Moderate disruption; buffer depleted, minor rescheduling required, no catastrophic line stops. |
| **HIGH** | `473` | `15.77%` | Severe disruption; production lines halted/throttled, substantial revenue at risk, expedited freight required. |
| **CRITICAL** | `179` | `5.97%` | Catastrophic failure; extended line shutdowns, extensive customer backlog, major EBITDA hit, contract renegotiation. |

> [!NOTE]
> **Target Imbalance Analysis**:
> The dataset exhibits realistic class imbalance: **Medium (39.50%)** and **Low (38.77%)** make up 78.27% of all cases, while **High (15.77%)** and **Critical (5.97%)** constitute the minority severe failure modes. Stratified train/test splitting and class-weighted / scale_pos_weight loss configurations are strictly required to ensure the model does not ignore rare critical failures.

---
## 2. Kept Pre-Disruption Features (Candidate Features to KEEP)

A total of **40 features** are retained. Every single retained feature represents an operational baseline, vendor assessment score, organizational maturity index, contract parameter, or pre-onset early warning signal that exists **prior to the event**.

| Idx | Feature Name | Data Type | Null Count | Unique | Semantic Description & Pre-Event Availability |
|---|---|---|---|---|---|
| 3 | `industry_sector` | `str` | `0` | `10` | Manufacturing sector (e.g., electronics, automotive, pharma). Establishes supply chain lead time and vulnerability baselines. |
| 9 | `disruption_category` | `str` | `0` | `10` | High-level category of incoming disruption threat/scenario being simulated or detected (e.g. cyber_attack, natural_disaster, supplier_failure). |
| 10 | `disruption_subcategory` | `str` | `0` | `17` | Granular scenario type of the impending disruption threat (e.g. quality_failure, capacity_reduction, financial_insolvency). |
| 13 | `affected_region` | `str` | `0` | `10` | Geographic macro-region of the supplier and supply link (e.g., Northeast_Asia, Western_Europe, Latin_America). |
| 17 | `supplier_tier` | `int64` | `0` | `4` | Contracted supply tier level of the vendor (Tier 1 direct, Tier 2 sub-component, Tier 3/4 raw material). |
| 18 | `supplier_criticality` | `str` | `0` | `5` | Pre-existing vendor criticality classification (preferred, approved, conditional, sole_source, strategic_partner). |
| 19 | `supplier_country` | `str` | `0` | `32` | Country ISO code of the vendor manufacturing site. |
| 20 | `supplier_geographic_risk_score` | `float64` | `0` | `691` | Normalized external geographic/geopolitical risk index of the supplier location (0 to 10 scale). |
| 21 | `number_of_alternative_suppliers` | `int64` | `0` | `8` | Count of pre-qualified, contracted alternative suppliers available in procurement directory. |
| 22 | `supplier_concentration_pct` | `float64` | `0` | `676` | Percentage of procurement spend/volume concentrated with this single vendor. |
| 23 | `affected_sku_count` | `int64` | `0` | `149` | Number of internal company SKUs dependent on this supplier component before disruption. |
| 24 | `affected_component_category` | `str` | `0` | `9` | Category of component supplied (e.g., electronic_component, energy, packaging, chemical, raw_material). |
| 25 | `supplier_financial_health_score` | `float64` | `0` | `625` | Pre-disruption credit and financial health rating (e.g., Altman Z / creditworthiness metric on 0-10 scale). |
| 26 | `supplier_audit_score_last` | `float64` | `0` | `533` | Score from the most recent supplier quality, compliance, and security audit (0 to 100). |
| 27 | `months_since_last_audit` | `int64` | `0` | `47` | Recency of the supplier audit in months (audit freshness / governance gap indicator). |
| 28 | `supplier_relationship_years` | `float64` | `0` | `285` | Tenure of commercial relationship with the vendor in years. |
| 29 | `dual_source_in_place` | `bool` | `0` | `2` | Boolean indicating whether a dual-sourcing arrangement was contracted prior to disruption. |
| 31 | `supply_volume_at_risk_units` | `int64` | `0` | `2996` | Standard expected delivery volume in units sourced from this vendor during an operating cycle. |
| 32 | `revenue_at_risk_usd` | `float64` | `0` | `3000` | Total product revenue exposed to this supplier component under baseline operations. |
| 45 | `inventory_buffer_days_at_onset` | `float64` | `0` | `687` | Days of buffer inventory maintained on-hand at the start of any period. |
| 47 | `normal_lead_time_days` | `float64` | `0` | `1069` | Standard contracted nominal lead time in days under normal operating conditions. |
| 51 | `logistics_mode_primary` | `str` | `0` | `7` | Standard contracted primary transport mode (ocean_freight, road, air_freight, rail, intermodal). |
| 56 | `freight_cost_normal_usd` | `float64` | `0` | `2908` | Standard baseline shipping cost under normal commercial terms. |
| 59 | `logistics_concentration_risk` | `str` | `0` | `4` | Carrier diversification profile (single_carrier, dual_carrier, multi_carrier, own_fleet). |
| 60 | `nearshoring_available` | `bool` | `0` | `2` | Boolean flag indicating whether an active nearshore production option exists. |
| 65 | `demand_volatility_index` | `float64` | `0` | `451` | Historical coefficient/index of demand volatility for products utilizing this component. |
| 66 | `demand_forecast_error_mape` | `float64` | `0` | `1258` | Baseline historical demand forecast error (Mean Absolute Percentage Error). |
| 67 | `order_variability_bullwhip_ratio` | `float64` | `0` | `368` | Historical bullwhip ratio measuring upstream order fluctuation amplification. |
| 68 | `customer_concentration_top3_pct` | `float64` | `0` | `501` | Percentage of customer demand accounted for by the top 3 buyers (downstream vulnerability). |
| 70 | `safety_stock_adequacy` | `str` | `0` | `4` | Pre-existing safety stock policy evaluation (adequate, marginal, insufficient, critical). |
| 89 | `early_warning_signal_detected` | `bool` | `0` | `2` | Boolean flag indicating whether automated early warning intelligence detected threat prior to onset. |
| 90 | `early_warning_source` | `str` | `0` | `6` | Source of advance warning (supplier_financial_monitoring, weather_forecast, news_sentiment, etc.). |
| 91 | `early_warning_lead_days` | `int64` | `0` | `56` | Days of advance notice provided by early warning system prior to physical event onset. |
| 92 | `supply_chain_visibility_score` | `float64` | `0` | `658` | End-to-end supply chain digital visibility index (0 to 5 scale). |
| 93 | `digital_twin_available` | `bool` | `0` | `2` | Boolean flag indicating whether a digital supply chain twin model exists for simulation. |
| 94 | `erp_alert_triggered` | `bool` | `0` | `2` | Boolean flag indicating whether ERP automated threshold monitoring fired an early alert. |
| 95 | `external_data_feed_active` | `bool` | `0` | `2` | Boolean flag indicating whether real-time external risk/logistics data feeds are enabled. |
| 96 | `tier2_visibility_flag` | `bool` | `0` | `2` | Boolean flag indicating whether the buyer has visibility into the vendor sub-tier suppliers. |
| 102 | `supply_chain_maturity_score` | `float64` | `0` | `387` | Organizational supply chain maturity rating (0 to 5 scale). |
| 103 | `resilience_posture_pre_event` | `str` | `0` | `5` | Organizational resilience readiness posture evaluated BEFORE the event (compliant, aware, proactive, adaptive, reactive). |

---
## 3. Removed Post-Disruption & Leakage Features (REMOVED)

A total of **61 features** are removed due to direct target leakage or post-disruption temporality.

| Idx | Feature Name | Data Type | Null Count | Reason for Exclusion (Leakage Rationale) |
|---|---|---|---|---|
| 12 | `severity_score` | `float64` | `0` | Direct continuous numerical proxy from which severity_level was derived. 100% target label duplication / instant leakage. |
| 7 | `event_duration_days` | `int64` | `0` | Total duration of the disruption event in days; only known after the event has completely concluded. |
| 8 | `detection_lag_days` | `int64` | `0` | Days elapsed between disruption start and detection; unfolds during the event. |
| 30 | `supply_volume_impact_pct` | `float64` | `0` | Percentage of supplier volume actually lost during the disruption event; direct consequence metric. |
| 33 | `actual_revenue_loss_usd` | `float64` | `0` | Actual realized financial revenue loss caused by the disruption; primary post-event financial consequence. |
| 34 | `ebitda_impact_usd` | `float64` | `0` | Realized EBITDA impact resulting from the disruption; post-event financial consequence. |
| 35 | `stockout_occurred` | `bool` | `0` | Boolean flag indicating whether inventory was exhausted during the disruption; direct consequence. |
| 36 | `stockout_duration_days` | `int64` | `0` | Number of days the facility suffered a stockout; post-event consequence metric. |
| 37 | `production_lines_halted` | `int64` | `0` | Count of factory assembly lines completely halted during the disruption; operational impact consequence. |
| 38 | `production_lines_throttled` | `int64` | `0` | Count of factory assembly lines throttled/slowed during the disruption; operational impact consequence. |
| 39 | `throughput_loss_units` | `int64` | `0` | Realized volume of factory throughput lost during disruption; post-event consequence. |
| 40 | `throughput_loss_pct` | `float64` | `0` | Percentage of manufacturing throughput lost during disruption; post-event consequence. |
| 41 | `demand_fulfilled_pct` | `float64` | `0` | Realized percentage of customer demand fulfilled during the disruption; post-event consequence. |
| 42 | `customer_order_backlog_units` | `int64` | `0` | Quantity of customer orders pushed into backlog during the event; post-event consequence. |
| 43 | `expediting_cost_usd` | `float64` | `0` | Emergency expediting fees paid to avert/mitigate shortages; post-event emergency spend. |
| 44 | `cost_of_disruption_total_usd` | `float64` | `0` | Total financial cost and economic damage caused by the disruption; post-event financial consequence. |
| 48 | `disrupted_lead_time_days` | `float64` | `0` | Actual lead time experienced during transit under disruption; consequence of the event. |
| 49 | `lead_time_extension_days` | `float64` | `0` | Number of additional days the shipment was delayed; direct consequence of the event. |
| 50 | `lead_time_extension_pct` | `float64` | `0` | Percentage lead time delay experienced during the disruption; direct consequence. |
| 52 | `logistics_mode_disrupted` | `bool` | `0` | Boolean indicating whether the primary logistics route was disrupted during the event; consequence. |
| 53 | `port_of_entry_congestion_flag` | `bool` | `0` | Boolean indicating whether congestion occurred at the entry port during the event; realized condition. |
| 54 | `customs_clearance_delay_days` | `float64` | `0` | Days delayed at customs during the disruption event; consequence of the event. |
| 55 | `carrier_failure_flag` | `bool` | `0` | Boolean indicating whether the freight carrier suffered a failure during transit; realized event failure. |
| 57 | `freight_cost_disrupted_usd` | `float64` | `0` | Actual freight cost incurred during the disrupted transit; post-event operational spend. |
| 58 | `freight_cost_premium_usd` | `float64` | `0` | Premium freight surcharge incurred due to the disruption; post-event operational spend. |
| 61 | `demand_shock_type` | `str` | `0` | Type of demand shock that manifested during or after the disruption; realized event characteristic. |
| 62 | `demand_shock_trigger` | `str` | `0` | Specific trigger of the demand shock that occurred during the event; realized event characteristic. |
| 63 | `demand_spike_magnitude_pct` | `float64` | `0` | Realized percentage increase in demand during the shock event; post-event metric. |
| 64 | `demand_crash_magnitude_pct` | `float64` | `0` | Realized percentage decrease in demand during the shock event; post-event metric. |
| 69 | `channel_shift_flag` | `bool` | `0` | Flag indicating whether customers shifted purchase channels during the disruption; reactive outcome. |
| 71 | `mitigation_strategy_primary` | `str` | `0` | Reactive emergency tactical response selected by management to counter the disruption; post-event action. |
| 72 | `mitigation_strategy_secondary` | `str` | `0` | Secondary reactive tactical response selected during the crisis; post-event action. |
| 73 | `mitigation_activation_lag_days` | `int64` | `0` | Days elapsed before emergency mitigation was activated; post-event response metric. |
| 74 | `mitigation_effectiveness_score` | `float64` | `0` | Retrospective evaluation score of how effective the mitigation was; post-event audit metric. |
| 75 | `spot_buy_activated` | `bool` | `0` | Flag indicating whether emergency spot market purchases were executed; reactive response. |
| 76 | `spot_buy_volume_units` | `int64` | `0` | Quantity of units procured on the emergency spot market; reactive response. |
| 77 | `spot_buy_premium_pct` | `float64` | `0` | Price premium percentage paid for emergency spot buys; reactive response metric. |
| 78 | `alternative_supplier_onboarded` | `bool` | `0` | Flag indicating whether an emergency replacement supplier was onboarded (98.4% missing/False); reactive response. |
| 79 | `onboarding_time_days` | `float64` | `2951` | Days taken to onboard emergency backup supplier (98.4% missing); post-event response metric. |
| 80 | `customer_allocation_applied` | `bool` | `0` | Flag indicating whether customer order rationing was applied; reactive management action. |
| 81 | `demand_shaping_discount_pct` | `float64` | `0` | Emergency discount percentage offered to placate customers; reactive management action. |
| 82 | `safety_stock_policy_changed` | `bool` | `0` | Flag indicating whether safety stock policy was modified in reaction to the event; post-event policy change. |
| 83 | `new_safety_stock_days` | `float64` | `2693` | Revised safety stock level enacted following the disruption (89.8% missing); post-event outcome. |
| 84 | `resilience_investment_triggered` | `bool` | `0` | Flag indicating whether capital expenditure for resilience was approved after the event; post-event action. |
| 85 | `resilience_investment_usd` | `float64` | `2684` | Capex amount invested into resilience after the event (89.5% missing); post-event outcome. |
| 86 | `recovery_trajectory` | `str` | `0` | Mathematical curve/pattern of the recovery process (e.g., V-shaped, U-shaped); post-event lifecycle metric. |
| 87 | `time_to_50pct_recovery_days` | `int64` | `0` | Days required for the operation to recover to 50% capacity; post-event recovery metric. |
| 88 | `time_to_full_recovery_days` | `int64` | `0` | Days required to reach 100% complete recovery; post-event recovery metric. |
| 97 | `bcp_activated` | `bool` | `0` | Flag indicating whether formal Business Continuity Plan was activated; post-event emergency response. |
| 98 | `crisis_team_convened` | `bool` | `0` | Flag indicating whether executive crisis management team was convened; post-event emergency response. |
| 99 | `war_room_duration_days` | `int64` | `0` | Number of days the emergency war room remained operational; post-event response metric. |
| 100 | `insurance_claim_filed` | `bool` | `0` | Flag indicating whether an insurance claim was submitted; post-event financial recovery action. |
| 101 | `insurance_payout_usd` | `float64` | `2825` | Amount of insurance compensation collected (94.2% missing); post-event financial settlement. |
| 104 | `resilience_posture_post_event` | `str` | `0` | Organizational resilience posture evaluated AFTER the disruption concluded; post-event assessment. |
| 105 | `root_cause_category` | `str` | `0` | Root cause determined during post-incident investigation; post-mortem analysis classification. |
| 106 | `preventability_score` | `float64` | `0` | Score assessing whether the incident could have been prevented; post-mortem audit metric. |
| 107 | `repeat_event_flag` | `bool` | `0` | Flag indicating whether this represents a recurrence of a previous failure; post-mortem audit metric. |
| 108 | `post_event_supplier_status` | `str` | `0` | Final vendor relationship disposition after the incident (e.g. terminated, under review); post-event outcome. |
| 109 | `near_miss_flag` | `bool` | `0` | Post-incident review classification indicating if the event was nearly avoided; post-mortem tag. |
| 110 | `lessons_learned_documented` | `bool` | `0` | Flag indicating whether formal post-incident lessons learned report was produced; post-mortem governance. |
| 111 | `industry_event_flag` | `bool` | `0` | Post-mortem classification of whether the disruption impacted the broader industry; post-mortem tag. |

---
## 4. Identifiers, Constants, and Non-Predictive Columns (REMOVED)

A total of **11 features** are dropped because they are arbitrary primary keys, administrative date strings, zero-variance constants, or redundant clones.

| Idx | Column Name | Data Type | Null Count | Reason for Exclusion |
|---|---|---|---|---|
| 0 | `event_id` | `str` | `0` | Primary key identifier for the disruption event row. Arbitrary unique ID with no predictive generalizability. |
| 1 | `company_id` | `str` | `0` | Entity identifier for the internal reporting manufacturing company. High cardinality administrative tag. |
| 2 | `plant_id` | `str` | `0` | Entity identifier for the specific manufacturing facility. Administrative routing tag. |
| 15 | `supplier_id` | `str` | `0` | Entity identifier for the vendor. Arbitrary code (SUP-XXXX) with no intrinsic risk meaning. |
| 16 | `supplier_name_synthetic` | `str` | `0` | Synthetic text name of the vendor. High cardinality string with no predictive signal. |
| 112 | `sku` | `str` | `0` | Constant value ("MFG-006") across all 3000 rows (zero variance). Contains no predictive information. |
| 4 | `event_detection_date` | `str` | `0` | Administrative timestamp string marking when the event was detected. |
| 5 | `event_start_date` | `str` | `0` | Administrative timestamp string marking when the disruption started. |
| 6 | `event_resolution_date` | `str` | `0` | Post-disruption timestamp string marking when the event was fully resolved. |
| 46 | `inventory_depletion_date` | `str` | `2437` | Post-disruption outcome timestamp marking when inventory reached zero (81.2% missing; only exists if stockout occurred). |
| 14 | `affected_country` | `str` | `0` | 100% duplicate clone of supplier_country (identical values across all 3000 rows). Collinear redundancy. |

---
## 5. Summary and Proposed Modeling Specification

### Proposed Final X and y

- **X (Input Feature Matrix)**: 40 pre-disruption features (comprising 22 numerical metrics, 11 categorical descriptors, and 7 boolean indicators).
- **y (Target Vector)**: `severity_level` (Categorical: `low`, `medium`, `high`, `critical`).

### Missing Value Strategy
- In the 40 retained pre-disruption features, there are **0 missing values** (`100% complete data`).
- The only columns in the entire CSV with missing values are the 5 post-disruption columns (`inventory_depletion_date`, `onboarding_time_days`, `new_safety_stock_days`, `resilience_investment_usd`, `insurance_payout_usd`), all of which have been properly identified as leakage and removed.

### Verification Checklist
- [x] Zero post-disruption variables in X
- [x] Target proxy `severity_score` completely removed
- [x] No arbitrary entity IDs used as numerical features
- [x] Constant column `sku` removed
- [x] Redundant clone `affected_country` removed in favor of `supplier_country`
- [x] All 113 columns explicitly classified with documented reasons