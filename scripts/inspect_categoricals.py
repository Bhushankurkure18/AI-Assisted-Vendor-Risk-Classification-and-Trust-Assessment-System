import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

# Let's inspect unique values of categorical columns and value descriptions
cats = df.select_dtypes(include=['object', 'bool']).columns
print(f"Categorical and boolean columns ({len(cats)}):")
for col in cats:
    print(f"\n--- {col} ({df[col].dtype}) ---")
    val_counts = df[col].value_counts(dropna=False).head(10).to_dict()
    print(val_counts)
