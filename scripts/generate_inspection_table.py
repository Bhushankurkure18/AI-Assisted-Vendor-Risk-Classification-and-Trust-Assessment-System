import json
import pandas as pd

df = pd.read_csv('data/raw/mfg006_disruptions.csv')

with open('column_inspection.json') as f:
    cols = json.load(f)

lines = []
lines.append(f"# MFG006 Dataset Full Column Inspection (Total {len(cols)} columns)\n")
lines.append(f"Total Rows: {len(df)}")
lines.append(f"Total Columns: {len(df.columns)}")
lines.append(f"Duplicates: {df.duplicated().sum()}\n")
lines.append("## Target Distribution ('severity_level'):")
counts = df['severity_level'].value_counts(dropna=False)
pcts = (df['severity_level'].value_counts(normalize=True, dropna=False) * 100).round(2)
for k in counts.index:
    lines.append(f"- **{k}**: {counts[k]} ({pcts[k]}%)")

lines.append("\n## All Columns Details:\n")
lines.append("| Idx | Column Name | Dtype | Missing | Missing % | Unique | Sample Values |")
lines.append("|---|---|---|---|---|---|---|")

for c in cols:
    samples_str = str(c['samples'])[:50].replace('|', '/')
    lines.append(f"| {c['index']} | `{c['column']}` | {c['dtype']} | {c['missing']} | {c['missing_pct']}% | {c['nunique']} | {samples_str} |")

with open('docs_column_table.md', 'w') as f:
    f.write("\n".join(lines))

print("Successfully written docs_column_table.md")
