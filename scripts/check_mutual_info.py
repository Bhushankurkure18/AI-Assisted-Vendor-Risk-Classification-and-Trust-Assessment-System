import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

X_temp = df.drop(columns=['severity_level', 'severity_score', 'event_id', 'company_id', 'plant_id', 'supplier_id', 'supplier_name_synthetic', 'sku'], errors='ignore')

for c in X_temp.columns:
    if 'date' in c:
        X_temp = X_temp.drop(columns=[c])
    elif X_temp[c].dtype.kind in ('O', 'U', 'S', 'b'):  # object, unicode string, bool
        X_temp[c] = pd.factorize(X_temp[c])[0]
    else:
        X_temp[c] = X_temp[c].fillna(-1)

# Ensure all columns are numeric
for c in X_temp.columns:
    X_temp[c] = pd.to_numeric(X_temp[c], errors='coerce').fillna(-1)

y_encoded, y_cats = pd.factorize(df['severity_level'])

mi = mutual_info_classif(X_temp, y_encoded, random_state=42)
mi_series = pd.Series(mi, index=X_temp.columns).sort_values(ascending=False)

print("\nTop 40 Features by Mutual Information with severity_level:")
for idx, (col, val) in enumerate(mi_series.head(40).items()):
    print(f"{idx+1:2d}. {col:<40} : {val:.4f}")

print("\nBottom 20 Features by Mutual Information with severity_level:")
for idx, (col, val) in enumerate(mi_series.tail(20).items()):
    print(f"{idx+1:2d}. {col:<40} : {val:.4f}")
