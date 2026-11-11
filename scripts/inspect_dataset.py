
import json
import pandas as pd

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"Duplicates: {df.duplicated().sum()}")
print("\nTarget 'severity_level' value counts:")
print(df['severity_level'].value_counts(dropna=False))
print("\nTarget percentages:")
print((df['severity_level'].value_counts(normalize=True, dropna=False) * 100).round(2))

with open('column_inspection.json') as f:
    cols = json.load(f)

print("\n" + "="*110)
print(f"{'Idx':<4} {'Column Name':<42} {'Dtype':<10} {'Missing':<10} {'Unique':<8} {'Sample Values'}")
print("="*110)
for c in cols:
    samples_str = str(c['samples'])[:45]
    print(f"{c['index']:<4} {c['column']:<42} {c['dtype']:<10} {c['missing']:<10} {c['nunique']:<8} {samples_str}")
