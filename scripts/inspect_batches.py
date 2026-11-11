import pandas as pd
import json

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

# Let's inspect all columns systematically
print("Total columns:", len(df.columns))

# Let's print out the columns in logical batches
for start in range(0, len(df.columns), 20):
    end = min(start + 20, len(df.columns))
    print(f"\n--- Batch {start} to {end-1} ---")
    for idx in range(start, end):
        col = df.columns[idx]
        val_sample = df[col].dropna().unique()[:3].tolist()
        print(f"{idx:3d}. {col} | {df[col].dtype} | nulls: {df[col].isna().sum()} | unq: {df[col].nunique()} | eg: {val_sample}")
