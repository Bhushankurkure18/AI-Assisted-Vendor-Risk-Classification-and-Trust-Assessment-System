import pandas as pd

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

print("Revenue at risk vs actual revenue loss:")
print(df[['revenue_at_risk_usd', 'actual_revenue_loss_usd', 'severity_score', 'severity_level']].head(10))

print("\nRatio of actual loss to revenue at risk:")
ratio = df['actual_revenue_loss_usd'] / df['revenue_at_risk_usd']
print(ratio.describe())

print("\nSupply volume at risk vs supply volume impact pct:")
print(df[['supply_volume_at_risk_units', 'supply_volume_impact_pct', 'severity_score']].head(10))
