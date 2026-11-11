# MFG006 Model Explainability & Feature Attribution Report

This document details the feature attribution architecture for the structured machine learning models. It answers: **Why did the model classify a vendor into a given disruption severity tier?**

## 1. Top 20 Global Feature Drivers (Random Forest & XGBoost)

| Rank | Feature Identifier | Clean Name | RF Importance (MDI) | XGBoost Importance (Gain) | Mean Importance |
|---|---|---|---|---|---|
| 1 | `num__revenue_at_risk_usd` | **revenue_at_risk_usd** | `0.2259` | `0.0295` | `**0.1277**` |
| 2 | `num__supplier_concentration_pct` | **supplier_concentration_pct** | `0.0513` | `0.0164` | `**0.0338**` |
| 3 | `num__inventory_buffer_days_at_onset` | **inventory_buffer_days_at_onset** | `0.0277` | `0.0133` | `**0.0205**` |
| 4 | `num__demand_forecast_error_mape` | **demand_forecast_error_mape** | `0.0273` | `0.0077` | `**0.0175**` |
| 5 | `num__buffer_to_lead_time_ratio` | **buffer_to_lead_time_ratio** | `0.0271` | `0.0072` | `**0.0171**` |
| 6 | `num__demand_volatility_index` | **demand_volatility_index** | `0.0258` | `0.0072` | `**0.0165**` |
| 7 | `num__customer_concentration_top3_pct` | **customer_concentration_top3_pct** | `0.0255` | `0.0072` | `**0.0163**` |
| 8 | `num__supplier_geographic_risk_score` | **supplier_geographic_risk_score** | `0.0259` | `0.0067` | `**0.0163**` |
| 9 | `num__order_variability_bullwhip_ratio` | **order_variability_bullwhip_ratio** | `0.0248` | `0.0066` | `**0.0157**` |
| 10 | `cat__disruption_category_supplier_failure` | **disruption_category_supplier_failure** | `0.0090` | `0.0220` | `**0.0155**` |
| 11 | `num__normal_lead_time_days` | **normal_lead_time_days** | `0.0231` | `0.0061` | `**0.0146**` |
| 12 | `cat__disruption_subcategory_customs_delay` | **disruption_subcategory_customs_delay** | `0.0030` | `0.0257` | `**0.0143**` |
| 13 | `num__freight_cost_normal_usd` | **freight_cost_normal_usd** | `0.0235` | `0.0049` | `**0.0142**` |
| 14 | `num__supplier_audit_score_last` | **supplier_audit_score_last** | `0.0234` | `0.0048` | `**0.0141**` |
| 15 | `num__affected_sku_count` | **affected_sku_count** | `0.0230` | `0.0047` | `**0.0138**` |
| 16 | `num__supplier_financial_health_score` | **supplier_financial_health_score** | `0.0232` | `0.0043` | `**0.0137**` |
| 17 | `num__supply_volume_at_risk_units` | **supply_volume_at_risk_units** | `0.0224` | `0.0049` | `**0.0137**` |
| 18 | `num__supplier_risk_index` | **supplier_risk_index** | `0.0223` | `0.0050` | `**0.0137**` |
| 19 | `num__supplier_relationship_years` | **supplier_relationship_years** | `0.0216` | `0.0053` | `**0.0134**` |
| 20 | `num__audit_governance_risk` | **audit_governance_risk** | `0.0212` | `0.0051` | `**0.0132**` |

---

## 2. Key Domain Risk Drivers Identified

Across both Random Forest and XGBoost, the primary pre-disruption drivers of disruption severity are:

1. **`inventory_buffer_days_at_onset` & `buffer_to_lead_time_ratio`**: Facilities with lower buffer coverage relative to contracted lead times consistently trigger elevated disruption severity tiers.
2. **`supplier_concentration_pct` & `single_source_dependency_flag`**: High concentration with zero qualified backup suppliers is the dominant operational multiplier for High and Critical events.
3. **`revenue_at_risk_usd`**: Higher baseline revenue exposure strongly influences financial risk classification.
4. **`supplier_financial_health_score` & `supplier_risk_index`**: Financially vulnerable suppliers lack the capital buffer to maintain shipments during stress, leading directly to higher severity.
5. **`normal_lead_time_days` & `logistics_concentration_risk`**: Extended overseas lead times coupled with single-carrier reliance heighten transit delay risks.

---

## 3. Methodological Governance & Limitations

> [!IMPORTANT]

> **Correlation vs Causation**: Feature importance identifies statistical associations and variance splits in tree nodes; it does **not** prove strict causal mechanisms in physical manufacturing operations.
> Feature attribution outputs must be treated as decision-support indicators for procurement audits rather than deterministic proofs.
