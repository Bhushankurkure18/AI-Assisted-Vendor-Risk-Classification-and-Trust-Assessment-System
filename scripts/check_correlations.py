import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

# Numerical columns
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Let's compute correlation with severity_score
corrs = df[num_cols].corrwith(df['severity_score']).sort_values(ascending=False)

print("Top 25 Positive Correlations with severity_score:")
print(corrs.head(25))

print("\nTop 25 Negative Correlations with severity_score:")
print(corrs.tail(25))
