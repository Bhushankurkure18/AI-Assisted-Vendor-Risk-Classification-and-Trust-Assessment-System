# MFG006 Dataset Full Column Inspection (Total 113 columns)

Total Rows: 3000
Total Columns: 113
Duplicates: 0

## Target Distribution ('severity_level'):
- **medium**: 1185 (39.5%)
- **low**: 1163 (38.77%)
- **high**: 473 (15.77%)
- **critical**: 179 (5.97%)

## All Columns Details:

| Idx | Column Name | Dtype | Missing | Missing % | Unique | Sample Values |
|---|---|---|---|---|---|---|
| 0 | `event_id` | str | 0 | 0.0% | 3000 | ['SCE-2015-00001', 'SCE-2015-00002', 'SCE-2015-000 |
| 1 | `company_id` | str | 0 | 0.0% | 30 | ['MFG-CO-007', 'MFG-CO-001', 'MFG-CO-028'] |
| 2 | `plant_id` | str | 0 | 0.0% | 90 | ['PLT-054', 'PLT-074', 'PLT-020'] |
| 3 | `industry_sector` | str | 0 | 0.0% | 10 | ['electronics', 'industrial', 'automotive'] |
| 4 | `event_detection_date` | str | 0 | 0.0% | 2017 | ['2022-10-08', '2016-11-09', '2020-03-06'] |
| 5 | `event_start_date` | str | 0 | 0.0% | 2051 | ['2022-10-06', '2016-11-02', '2020-03-02'] |
| 6 | `event_resolution_date` | str | 0 | 0.0% | 2046 | ['2022-11-06', '2016-11-21', '2020-03-07'] |
| 7 | `event_duration_days` | int64 | 0 | 0.0% | 200 | [31, 19, 5] |
| 8 | `detection_lag_days` | int64 | 0 | 0.0% | 49 | [2, 7, 4] |
| 9 | `disruption_category` | str | 0 | 0.0% | 10 | ['cyber_attack', 'quality_recall', 'supplier_failu |
| 10 | `disruption_subcategory` | str | 0 | 0.0% | 17 | ['data_breach', 'quality_failure', 'seasonal_ampli |
| 11 | `severity_level` | str | 0 | 0.0% | 4 | ['high', 'medium', 'low'] |
| 12 | `severity_score` | float64 | 0 | 0.0% | 789 | [6.25, 4.64, 1.96] |
| 13 | `affected_region` | str | 0 | 0.0% | 10 | ['Northeast_Asia', 'South_Asia', 'Western_Europe'] |
| 14 | `affected_country` | str | 0 | 0.0% | 32 | ['JP', 'BD', 'FR'] |
| 15 | `supplier_id` | str | 0 | 0.0% | 1905 | ['SUP-1819', 'SUP-2015', 'SUP-2392'] |
| 16 | `supplier_name_synthetic` | str | 0 | 0.0% | 2848 | ['Meridian Parts Co 1819', 'AlphaLink Supply 2015' |
| 17 | `supplier_tier` | int64 | 0 | 0.0% | 4 | [2, 1, 4] |
| 18 | `supplier_criticality` | str | 0 | 0.0% | 5 | ['preferred', 'conditional', 'strategic_partner'] |
| 19 | `supplier_country` | str | 0 | 0.0% | 32 | ['JP', 'BD', 'FR'] |
| 20 | `supplier_geographic_risk_score` | float64 | 0 | 0.0% | 691 | [2.96, 6.14, 2.16] |
| 21 | `number_of_alternative_suppliers` | int64 | 0 | 0.0% | 8 | [0, 1, 3] |
| 22 | `supplier_concentration_pct` | float64 | 0 | 0.0% | 676 | [80.1, 64.5, 61.5] |
| 23 | `affected_sku_count` | int64 | 0 | 0.0% | 149 | [74, 12, 22] |
| 24 | `affected_component_category` | str | 0 | 0.0% | 9 | ['energy', 'packaging', 'IT_service'] |
| 25 | `supplier_financial_health_score` | float64 | 0 | 0.0% | 625 | [7.19, 8.41, 3.48] |
| 26 | `supplier_audit_score_last` | float64 | 0 | 0.0% | 533 | [57.6, 28.7, 88.9] |
| 27 | `months_since_last_audit` | int64 | 0 | 0.0% | 47 | [17, 31, 24] |
| 28 | `supplier_relationship_years` | float64 | 0 | 0.0% | 285 | [7.9, 2.1, 5.3] |
| 29 | `dual_source_in_place` | bool | 0 | 0.0% | 2 | [0, 1] |
| 30 | `supply_volume_impact_pct` | float64 | 0 | 0.0% | 819 | [45.2, 26.3, 38.3] |
| 31 | `supply_volume_at_risk_units` | int64 | 0 | 0.0% | 2996 | [883284, 444903, 940169] |
| 32 | `revenue_at_risk_usd` | float64 | 0 | 0.0% | 3000 | [15505951.0, 602189.0, 674376.0] |
| 33 | `actual_revenue_loss_usd` | float64 | 0 | 0.0% | 2981 | [3252032.0, 69179.0, 158278.0] |
| 34 | `ebitda_impact_usd` | float64 | 0 | 0.0% | 2992 | [1309080.0, 24604.0, 89080.0] |
| 35 | `stockout_occurred` | bool | 0 | 0.0% | 2 | [0, 1] |
| 36 | `stockout_duration_days` | int64 | 0 | 0.0% | 125 | [0, 12, 35] |
| 37 | `production_lines_halted` | int64 | 0 | 0.0% | 10 | [2, 0, 1] |
| 38 | `production_lines_throttled` | int64 | 0 | 0.0% | 20 | [2, 7, 0] |
| 39 | `throughput_loss_units` | int64 | 0 | 0.0% | 2977 | [78945, 33837, 125204] |
| 40 | `throughput_loss_pct` | float64 | 0 | 0.0% | 629 | [29.4, 16.3, 30.8] |
| 41 | `demand_fulfilled_pct` | float64 | 0 | 0.0% | 512 | [76.5, 87.0, 75.4] |
| 42 | `customer_order_backlog_units` | int64 | 0 | 0.0% | 2851 | [20952, 4559, 22136] |
| 43 | `expediting_cost_usd` | float64 | 0 | 0.0% | 2964 | [439035.0, 3505.0, 7302.0] |
| 44 | `cost_of_disruption_total_usd` | float64 | 0 | 0.0% | 2996 | [3952883.0, 77605.0, 183396.0] |
| 45 | `inventory_buffer_days_at_onset` | float64 | 0 | 0.0% | 687 | [12.6, 15.2, 20.6] |
| 46 | `inventory_depletion_date` | str | 2437 | 81.23% | 529 | ['2015-07-09', '2018-02-27', '2019-05-10'] |
| 47 | `normal_lead_time_days` | float64 | 0 | 0.0% | 1069 | [85.6, 51.5, 111.1] |
| 48 | `disrupted_lead_time_days` | float64 | 0 | 0.0% | 1466 | [128.8, 68.1, 128.2] |
| 49 | `lead_time_extension_days` | float64 | 0 | 0.0% | 735 | [43.2, 16.6, 17.1] |
| 50 | `lead_time_extension_pct` | float64 | 0 | 0.0% | 898 | [50.5, 32.3, 15.4] |
| 51 | `logistics_mode_primary` | str | 0 | 0.0% | 7 | ['ocean_freight', 'air_freight', 'road'] |
| 52 | `logistics_mode_disrupted` | bool | 0 | 0.0% | 2 | [1, 0] |
| 53 | `port_of_entry_congestion_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 54 | `customs_clearance_delay_days` | float64 | 0 | 0.0% | 238 | [3.4, 1.8, 4.8] |
| 55 | `carrier_failure_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 56 | `freight_cost_normal_usd` | float64 | 0 | 0.0% | 2908 | [15771.0, 43755.0, 8457.0] |
| 57 | `freight_cost_disrupted_usd` | float64 | 0 | 0.0% | 2956 | [104028.0, 47666.0, 8730.0] |
| 58 | `freight_cost_premium_usd` | float64 | 0 | 0.0% | 2775 | [88257.0, 3911.0, 273.0] |
| 59 | `logistics_concentration_risk` | str | 0 | 0.0% | 4 | ['own_fleet', 'single_carrier', 'dual_carrier'] |
| 60 | `nearshoring_available` | bool | 0 | 0.0% | 2 | [0, 1] |
| 61 | `demand_shock_type` | str | 0 | 0.0% | 4 | ['no_demand_shock', 'demand_crash', 'demand_volati |
| 62 | `demand_shock_trigger` | str | 0 | 0.0% | 7 | ['none', 'seasonal_amplification', 'macro_economic |
| 63 | `demand_spike_magnitude_pct` | float64 | 0 | 0.0% | 439 | [0.0, 15.4, 24.8] |
| 64 | `demand_crash_magnitude_pct` | float64 | 0 | 0.0% | 170 | [0.0, 45.0, 28.0] |
| 65 | `demand_volatility_index` | float64 | 0 | 0.0% | 451 | [16.7, 32.7, 18.9] |
| 66 | `demand_forecast_error_mape` | float64 | 0 | 0.0% | 1258 | [57.0, 72.2, 120.3] |
| 67 | `order_variability_bullwhip_ratio` | float64 | 0 | 0.0% | 368 | [4.03, 2.03, 1.5] |
| 68 | `customer_concentration_top3_pct` | float64 | 0 | 0.0% | 501 | [21.2, 67.8, 51.1] |
| 69 | `channel_shift_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 70 | `safety_stock_adequacy` | str | 0 | 0.0% | 4 | ['adequate', 'insufficient', 'critical'] |
| 71 | `mitigation_strategy_primary` | str | 0 | 0.0% | 12 | ['inventory_build', 'demand_shaping', 'product_sub |
| 72 | `mitigation_strategy_secondary` | str | 0 | 0.0% | 13 | ['nothing', 'nearshoring', 'inventory_build'] |
| 73 | `mitigation_activation_lag_days` | int64 | 0 | 0.0% | 21 | [14, 6, 17] |
| 74 | `mitigation_effectiveness_score` | float64 | 0 | 0.0% | 592 | [4.2, 4.54, 2.34] |
| 75 | `spot_buy_activated` | bool | 0 | 0.0% | 2 | [0, 1] |
| 76 | `spot_buy_volume_units` | int64 | 0 | 0.0% | 568 | [0, 9852, 46452] |
| 77 | `spot_buy_premium_pct` | float64 | 0 | 0.0% | 521 | [0.0, 165.5, 96.2] |
| 78 | `alternative_supplier_onboarded` | bool | 0 | 0.0% | 2 | [0, 1] |
| 79 | `onboarding_time_days` | float64 | 2951 | 98.37% | 40 | [30.0, 152.0, 153.0] |
| 80 | `customer_allocation_applied` | bool | 0 | 0.0% | 2 | [0, 1] |
| 81 | `demand_shaping_discount_pct` | float64 | 0 | 0.0% | 178 | [0.0, 6.3, 22.2] |
| 82 | `safety_stock_policy_changed` | bool | 0 | 0.0% | 2 | [1, 0] |
| 83 | `new_safety_stock_days` | float64 | 2693 | 89.77% | 237 | [57.1, 34.9, 76.7] |
| 84 | `resilience_investment_triggered` | bool | 0 | 0.0% | 2 | [1, 0] |
| 85 | `resilience_investment_usd` | float64 | 2684 | 89.47% | 316 | [4304868.0, 3196699.0, 3920273.0] |
| 86 | `recovery_trajectory` | str | 0 | 0.0% | 5 | ['u_shaped', 'v_shaped', 'w_shaped'] |
| 87 | `time_to_50pct_recovery_days` | int64 | 0 | 0.0% | 177 | [23, 6, 1] |
| 88 | `time_to_full_recovery_days` | int64 | 0 | 0.0% | 253 | [46, 10, 2] |
| 89 | `early_warning_signal_detected` | bool | 0 | 0.0% | 2 | [0, 1] |
| 90 | `early_warning_source` | str | 0 | 0.0% | 6 | ['none', 'supplier_financial_monitoring', 'weather |
| 91 | `early_warning_lead_days` | int64 | 0 | 0.0% | 56 | [0, 1, 26] |
| 92 | `supply_chain_visibility_score` | float64 | 0 | 0.0% | 658 | [3.62, 4.56, 2.77] |
| 93 | `digital_twin_available` | bool | 0 | 0.0% | 2 | [0, 1] |
| 94 | `erp_alert_triggered` | bool | 0 | 0.0% | 2 | [0, 1] |
| 95 | `external_data_feed_active` | bool | 0 | 0.0% | 2 | [0, 1] |
| 96 | `tier2_visibility_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 97 | `bcp_activated` | bool | 0 | 0.0% | 2 | [0, 1] |
| 98 | `crisis_team_convened` | bool | 0 | 0.0% | 2 | [0, 1] |
| 99 | `war_room_duration_days` | int64 | 0 | 0.0% | 47 | [0, 6, 37] |
| 100 | `insurance_claim_filed` | bool | 0 | 0.0% | 2 | [1, 0] |
| 101 | `insurance_payout_usd` | float64 | 2825 | 94.17% | 175 | [94462.0, 809643.0, 1532094.0] |
| 102 | `supply_chain_maturity_score` | float64 | 0 | 0.0% | 387 | [2.4, 2.82, 1.53] |
| 103 | `resilience_posture_pre_event` | str | 0 | 0.0% | 5 | ['compliant', 'aware', 'proactive'] |
| 104 | `resilience_posture_post_event` | str | 0 | 0.0% | 5 | ['proactive', 'compliant', 'aware'] |
| 105 | `root_cause_category` | str | 0 | 0.0% | 9 | ['process_failure', 'logistics_fragility', 'poor_s |
| 106 | `preventability_score` | float64 | 0 | 0.0% | 645 | [6.08, 5.99, 4.19] |
| 107 | `repeat_event_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 108 | `post_event_supplier_status` | str | 0 | 0.0% | 5 | ['dual_sourced', 'under_review', 'retained'] |
| 109 | `near_miss_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 110 | `lessons_learned_documented` | bool | 0 | 0.0% | 2 | [1, 0] |
| 111 | `industry_event_flag` | bool | 0 | 0.0% | 2 | [0, 1] |
| 112 | `sku` | str | 0 | 0.0% | 1 | ['MFG-006'] |