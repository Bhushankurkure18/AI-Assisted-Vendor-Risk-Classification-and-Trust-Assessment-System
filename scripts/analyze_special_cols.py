import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

# Check which columns have missing values
missing_cols = df.columns[df.isna().any()].tolist()
print("Columns with missing values:")
for col in missing_cols:
    print(f"  {col}: {df[col].isna().sum()} missing ({df[col].isna().mean()*100:.2f}%)")

# Check if affected_country == supplier_country
print("\nIs affected_country identical to supplier_country?")
print((df['affected_country'] == df['supplier_country']).all())

# Check constant columns
constant_cols = [c for c in df.columns if df[c].nunique() <= 1]
print("\nConstant columns (nunique <= 1):", constant_cols)

# Check IDs / high cardinality strings
id_cols = [c for c in df.columns if df[c].nunique() > 2000 and df[c].dtype == 'object']
print("\nHigh cardinality text / IDs (>2000 unique):", id_cols)
