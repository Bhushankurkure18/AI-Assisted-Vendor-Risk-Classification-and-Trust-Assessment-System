"""
MFG006 Exploratory Data Analysis (EDA) Script.
Generates 11 publication-grade figures saved to reports/figures/mfg006/.
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set consistent plotting aesthetic
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 150
})

OUTPUT_DIR = BASE_DIR / "reports" / "figures" / "mfg006"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = BASE_DIR / "data" / "raw" / "mfg006_disruptions.csv"
df = pd.read_csv(DATA_PATH)

# Normalize target order
TARGET_ORDER = ["low", "medium", "high", "critical"]
PALETTE = {
    "low": "#2ecc71",       # Green
    "medium": "#3498db",    # Blue
    "high": "#e67e22",      # Orange
    "critical": "#e74c3c"   # Red
}

print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# -------------------------------------------------------------
# 1. Target Class Distribution
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
counts = df["severity_level"].value_counts().reindex(TARGET_ORDER)
pcts = (counts / len(df) * 100).round(1)

bars = ax.bar(TARGET_ORDER, counts, color=[PALETTE[c] for c in TARGET_ORDER], edgecolor="black", alpha=0.85)
for bar, count, pct in zip(bars, counts, pcts):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 20,
        f"{count}\n({pct}%)",
        ha="center",
        va="bottom",
        fontweight="bold"
    )

ax.set_title("MFG006 Target Class Distribution (severity_level)", fontweight="bold")
ax.set_xlabel("Disruption Severity Tier")
ax.set_ylabel("Number of Historical Events")
ax.set_ylim(0, max(counts) * 1.18)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_target_class_distribution.png")
plt.close()
print("Saved: 01_target_class_distribution.png")

# -------------------------------------------------------------
# 2. Numerical Feature Distributions
# -------------------------------------------------------------
num_sample_cols = [
    ("supplier_financial_health_score", "Financial Health (0-10)"),
    ("supplier_geographic_risk_score", "Geographic Risk (0-10)"),
    ("supplier_concentration_pct", "Concentration (%)"),
    ("inventory_buffer_days_at_onset", "Buffer Days at Onset"),
    ("normal_lead_time_days", "Normal Lead Time (Days)"),
    ("revenue_at_risk_usd", "Revenue at Risk (USD)")
]

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()

for idx, (col, title) in enumerate(num_sample_cols):
    ax = axes[idx]
    sns.histplot(df[col], kde=True, ax=ax, color="#2980b9", edgecolor="black", alpha=0.6)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Count")

plt.suptitle("Distributions of Key Pre-Disruption Risk Variables", fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_numerical_feature_distributions.png", bbox_inches="tight")
plt.close()
print("Saved: 02_numerical_feature_distributions.png")

# -------------------------------------------------------------
# 3. Supplier Financial Health by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=df,
    x="severity_level",
    y="supplier_financial_health_score",
    order=TARGET_ORDER,
    palette=PALETTE,
    ax=ax,
    boxprops=dict(alpha=0.85)
)
ax.set_title("Supplier Financial Health Score by Disruption Severity", fontweight="bold")
ax.set_xlabel("Disruption Severity Tier")
ax.set_ylabel("Financial Health Score (0.0 to 10.0)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_financial_health_by_severity.png")
plt.close()
print("Saved: 03_financial_health_by_severity.png")

# -------------------------------------------------------------
# 4. Supplier Geographic Risk by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=df,
    x="severity_level",
    y="supplier_geographic_risk_score",
    order=TARGET_ORDER,
    palette=PALETTE,
    ax=ax,
    boxprops=dict(alpha=0.85)
)
ax.set_title("Supplier Geographic Risk Score by Disruption Severity", fontweight="bold")
ax.set_xlabel("Disruption Severity Tier")
ax.set_ylabel("Geographic Risk Score (0.0 to 10.0)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_geographic_risk_by_severity.png")
plt.close()
print("Saved: 04_geographic_risk_by_severity.png")

# -------------------------------------------------------------
# 5. Supplier Criticality by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
ct_crit = pd.crosstab(df["supplier_criticality"], df["severity_level"])[TARGET_ORDER]
ct_crit_pct = ct_crit.div(ct_crit.sum(axis=1), axis=0) * 100

ct_crit_pct.plot(
    kind="bar",
    stacked=True,
    color=[PALETTE[c] for c in TARGET_ORDER],
    edgecolor="black",
    alpha=0.85,
    ax=ax
)
ax.set_title("Supplier Criticality Classification vs Severity Proportions", fontweight="bold")
ax.set_xlabel("Supplier Criticality Tier")
ax.set_ylabel("Percentage (%)")
ax.legend(title="Severity Tier", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_supplier_criticality_by_severity.png", bbox_inches="tight")
plt.close()
print("Saved: 05_supplier_criticality_by_severity.png")

# -------------------------------------------------------------
# 6. Number of Alternative Suppliers by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=df,
    x="severity_level",
    y="number_of_alternative_suppliers",
    order=TARGET_ORDER,
    palette=PALETTE,
    ax=ax,
    boxprops=dict(alpha=0.85)
)
ax.set_title("Number of Alternative Suppliers by Disruption Severity", fontweight="bold")
ax.set_xlabel("Disruption Severity Tier")
ax.set_ylabel("Available Pre-Qualified Alternative Suppliers")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "06_alternative_suppliers_by_severity.png")
plt.close()
print("Saved: 06_alternative_suppliers_by_severity.png")

# -------------------------------------------------------------
# 7. Audit Score by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=df,
    x="severity_level",
    y="supplier_audit_score_last",
    order=TARGET_ORDER,
    palette=PALETTE,
    ax=ax,
    boxprops=dict(alpha=0.85)
)
ax.set_title("Last Supplier Audit Score by Disruption Severity", fontweight="bold")
ax.set_xlabel("Disruption Severity Tier")
ax.set_ylabel("Audit Score (0 to 100)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "07_audit_score_by_severity.png")
plt.close()
print("Saved: 07_audit_score_by_severity.png")

# -------------------------------------------------------------
# 8. Supplier Concentration by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=df,
    x="severity_level",
    y="supplier_concentration_pct",
    order=TARGET_ORDER,
    palette=PALETTE,
    ax=ax,
    boxprops=dict(alpha=0.85)
)
ax.set_title("Supplier Sourcing Concentration (%) by Disruption Severity", fontweight="bold")
ax.set_xlabel("Disruption Severity Tier")
ax.set_ylabel("Supplier Concentration Percentage (%)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "08_supplier_concentration_by_severity.png")
plt.close()
print("Saved: 08_supplier_concentration_by_severity.png")

# -------------------------------------------------------------
# 9. Correlation Heatmap for Important Numerical Features
# -------------------------------------------------------------
heatmap_cols = [
    "supplier_tier",
    "supplier_geographic_risk_score",
    "number_of_alternative_suppliers",
    "supplier_concentration_pct",
    "supplier_financial_health_score",
    "supplier_audit_score_last",
    "months_since_last_audit",
    "supplier_relationship_years",
    "inventory_buffer_days_at_onset",
    "normal_lead_time_days",
    "demand_volatility_index",
    "demand_forecast_error_mape",
    "order_variability_bullwhip_ratio",
    "customer_concentration_top3_pct",
    "early_warning_lead_days",
    "supply_chain_visibility_score",
    "supply_chain_maturity_score"
]

fig, ax = plt.subplots(figsize=(12, 10))
corr = df[heatmap_cols].corr()
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="vlag",
    vmin=-0.4,
    vmax=0.4,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8},
    ax=ax
)
ax.set_title("Correlation Heatmap: Verified Pre-Disruption Numerical Features", fontweight="bold")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "09_numerical_correlation_heatmap.png", bbox_inches="tight")
plt.close()
print("Saved: 09_numerical_correlation_heatmap.png")

# -------------------------------------------------------------
# 10. Disruption Category by Severity
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ct_cat = pd.crosstab(df["disruption_category"], df["severity_level"])[TARGET_ORDER]
ct_cat.plot(
    kind="bar",
    color=[PALETTE[c] for c in TARGET_ORDER],
    edgecolor="black",
    alpha=0.85,
    ax=ax
)
ax.set_title("Historical Disruption Categories by Severity Tier", fontweight="bold")
ax.set_xlabel("Disruption Category")
ax.set_ylabel("Event Count")
ax.legend(title="Severity Tier")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "10_disruption_category_by_severity.png", bbox_inches="tight")
plt.close()
print("Saved: 10_disruption_category_by_severity.png")

# -------------------------------------------------------------
# 11. Outlier Analysis Boxplots
# -------------------------------------------------------------
outlier_cols = [
    "supplier_concentration_pct",
    "inventory_buffer_days_at_onset",
    "normal_lead_time_days",
    "demand_forecast_error_mape",
    "revenue_at_risk_usd",
    "supply_volume_at_risk_units"
]

# Standardize features for comparable boxplots
norm_df = df[outlier_cols].copy()
for col in outlier_cols:
    q25 = norm_df[col].quantile(0.25)
    q75 = norm_df[col].quantile(0.75)
    iqr = q75 - q25
    med = norm_df[col].median()
    norm_df[col] = (norm_df[col] - med) / (iqr if iqr > 0 else 1.0)

fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=norm_df, palette="Set2", ax=ax, fliersize=3)
ax.set_title("Outlier Analysis: Robust-Standardized Pre-Disruption Variables", fontweight="bold")
ax.set_ylabel("Standardized IQR Deviations from Median")
ax.set_xlabel("Operational Variable")
plt.xticks(rotation=25, ha="right")
plt.axhline(0, color="gray", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "11_outlier_analysis_boxplots.png", bbox_inches="tight")
plt.close()
print("Saved: 11_outlier_analysis_boxplots.png")

print(f"\nAll 11 EDA figures successfully generated in: {OUTPUT_DIR}")
