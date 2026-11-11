import pandas as pd
import json

df = pd.read_csv('data/raw/mfg006_disruptions.csv')
cols = df.columns.tolist()

# Define the classification of each column based on its actual semantic meaning and temporal availability

# 1. Target
target_cols = ['severity_level']

# 2. Target Equivalent / Label Proxy (Instant Leakage of Target)
target_proxy_cols = [
    'severity_score'  # Continuous score directly used to define severity_level
]

# 3. Identifiers / Non-Predictive / Metadata / Constants
identifier_and_constant_cols = [
    'event_id',                  # Unique event primary key (SCE-2015-00001...)
    'company_id',                # High-level internal company entity ID (MFG-CO-...)
    'plant_id',                  # Internal manufacturing plant entity ID (PLT-...)
    'supplier_id',               # Supplier entity ID (SUP-...)
    'supplier_name_synthetic',   # Synthetic company name string
    'sku',                       # Constant: 'MFG-006' for 100% of rows (zero variance)
    'event_detection_date',      # Timestamp string
    'event_start_date',          # Timestamp string
    'event_resolution_date',     # Timestamp string
    'inventory_depletion_date',  # Date string of stock depletion (post-event event, 81.2% missing)
    'affected_country',          # 100% redundant clone of supplier_country (identical values)
]

# 4. Post-Disruption Impact, Consequence, Recovery, and Mitigation (LEAKAGE)
# These represent variables only measurable or decided AFTER the disruption occurs
leakage_post_disruption_cols = [
    # Event progression & duration
    'event_duration_days',              # Total days the event lasted (resolution - start)
    'detection_lag_days',               # Days taken between start and detection

    # Direct operational damage / disruption impact
    'supply_volume_impact_pct',         # Actual supply volume lost/impacted during disruption
    'actual_revenue_loss_usd',          # Direct financial revenue lost due to disruption
    'ebitda_impact_usd',                 # EBITDA reduction caused by disruption
    'stockout_occurred',                # Flag whether inventory completely stocked out
    'stockout_duration_days',           # Days company was in stockout state
    'production_lines_halted',          # Number of production lines stopped
    'production_lines_throttled',       # Number of production lines slowed down
    'throughput_loss_units',            # Units of throughput lost
    'throughput_loss_pct',              # Percentage of production throughput lost
    'demand_fulfilled_pct',             # Actual demand fulfilled during the disruption
    'customer_order_backlog_units',      # Backlogged orders caused by disruption
    'expediting_cost_usd',              # Premium costs paid to expedite parts
    'cost_of_disruption_total_usd',      # Total aggregated financial damage

    # Logistics disruption consequences
    'disrupted_lead_time_days',         # Actual lead time experienced during disruption
    'lead_time_extension_days',         # Days added to lead time due to disruption
    'lead_time_extension_pct',          # % lead time increase during disruption
    'logistics_mode_disrupted',         # Whether shipping route was disrupted
    'port_of_entry_congestion_flag',     # Actual congestion encountered during event
    'customs_clearance_delay_days',     # Days delayed at customs during event
    'carrier_failure_flag',             # Whether carrier failed during transit
    'freight_cost_disrupted_usd',        # Freight cost paid during disruption
    'freight_cost_premium_usd',         # Premium freight paid due to disruption

    # Demand shock triggered by / during event
    'demand_shock_type',                # Observed shock during event
    'demand_shock_trigger',             # Specific trigger of shock during event
    'demand_spike_magnitude_pct',       # Realized demand spike % during event
    'demand_crash_magnitude_pct',       # Realized demand crash % during event
    'channel_shift_flag',               # Emergency channel shift during event

    # Mitigation & reactive interventions (post-event decisions)
    'mitigation_strategy_primary',      # Tactic chosen to respond to disruption
    'mitigation_strategy_secondary',    # Secondary response tactic
    'mitigation_activation_lag_days',   # Days taken to activate mitigation
    'mitigation_effectiveness_score',   # How effective the emergency response was
    'spot_buy_activated',               # Emergency spot purchases made
    'spot_buy_volume_units',            # Volume bought on emergency spot market
    'spot_buy_premium_pct',             # Premium paid for spot purchases
    'alternative_supplier_onboarded',   # Emergency onboarding of backup supplier
    'onboarding_time_days',             # Days taken to onboard emergency supplier
    'customer_allocation_applied',      # Rationing applied to customers
    'demand_shaping_discount_pct',      # Discounts offered to shape customer demand
    'safety_stock_policy_changed',      # Policy change made after event
    'new_safety_stock_days',            # New safety stock set after event
    'resilience_investment_triggered',   # Post-event capex investment triggered
    'resilience_investment_usd',        # Capex amount invested post-event

    # Recovery trajectory & duration
    'recovery_trajectory',              # Shape of recovery curve (V-shaped, U-shaped, etc.)
    'time_to_50pct_recovery_days',       # Days to recover 50% capacity
    'time_to_full_recovery_days',        # Days to achieve 100% recovery

    # Post-event response actions & governance
    'bcp_activated',                    # Business continuity plan activated
    'crisis_team_convened',             # Crisis team assembled for event
    'war_room_duration_days',           # Days war room operated
    'insurance_claim_filed',            # Insurance claim submitted
    'insurance_payout_usd',             # Payout received from insurance
    'resilience_posture_post_event',    # Organizational posture evaluated AFTER event
    'root_cause_category',              # Post-incident root cause classification
    'preventability_score',             # Post-incident review preventability score
    'repeat_event_flag',                # Post-incident review flag
    'post_event_supplier_status',       # Supplier status AFTER event (exited, retained...)
    'near_miss_flag',                   # Post-incident review flag
    'lessons_learned_documented',       # Post-incident review documentation flag
    'industry_event_flag'               # Post-incident classification
]

# Now let's examine the remaining candidate features:
classified_so_far = set(target_cols + target_proxy_cols + identifier_and_constant_cols + leakage_post_disruption_cols)
remaining_cols = [c for c in cols if c not in classified_so_far]

print(f"Total cols: {len(cols)}")
print(f"Target: {len(target_cols)}")
print(f"Target proxy: {len(target_proxy_cols)}")
print(f"Identifiers / constants: {len(identifier_and_constant_cols)}")
print(f"Leakage / post-disruption: {len(leakage_post_disruption_cols)}")
print(f"Remaining (Pre-Disruption Candidates): {len(remaining_cols)}")
print("\nRemaining Pre-Disruption Candidates:")
for idx, c in enumerate(remaining_cols):
    print(f"{idx+1:2d}. {c} | {df[c].dtype} | unq: {df[c].nunique()}")
