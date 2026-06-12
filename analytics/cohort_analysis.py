
import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("REDSHIFT_HOST"),
    port=os.getenv("REDSHIFT_PORT"),
    dbname=os.getenv("REDSHIFT_DB"),
    user=os.getenv("REDSHIFT_USER"),
    password=os.getenv("REDSHIFT_PASSWORD"),
    sslmode="require"
)
print("Connected to Redshift")

query = """
    SELECT
        customer_id, target, credit_amount,
        annuity_amount, income_total, debt_to_income_ratio,
        ext_source_mean, age_years, employment_years,
        income_type, education_type, region_rating
    FROM fact_loans
"""
df = pd.read_sql(query, conn)
conn.close()
print(f"Loaded {len(df):,} rows")

# ── Risk tier and income band ───────────────────────────────
df["risk_tier"] = pd.cut(
    df["ext_source_mean"],
    bins=[0, 0.4, 0.6, 1.0],
    labels=["High Risk", "Medium Risk", "Low Risk"]
)

df["income_band"] = pd.cut(
    df["income_total"],
    bins=[0, 90000, 180000, float("inf")],
    labels=["Low Income", "Mid Income", "High Income"]
)

df["age_band"] = pd.cut(
    df["age_years"],
    bins=[0, 30, 45, 60, 100],
    labels=["Under 30", "30-45", "45-60", "Over 60"]
)

# ── LTV calculation ─────────────────────────────────────────
df["ltv_score"] = (
    (1 - df["target"]) * df["credit_amount"] * 0.03
    - df["target"] * df["credit_amount"] * 0.45
)

# ── Cohort 1: Risk tier x Income band ──────────────────────
print("\n── Cohort 1: Risk Tier x Income Band ──")
cohort1 = df.groupby(["risk_tier", "income_band"]).agg(
    total_customers=("customer_id", "count"),
    default_rate=("target", "mean"),
    avg_ltv=("ltv_score", "mean"),
    avg_income=("income_total", "mean"),
    avg_credit=("credit_amount", "mean")
).round(2).reset_index()
cohort1 = cohort1.sort_values("avg_ltv", ascending=False)
print(cohort1.to_string(index=False))

# ── Cohort 2: Age band x Risk tier ─────────────────────────
print("\n── Cohort 2: Age Band x Risk Tier ──")
cohort2 = df.groupby(["age_band", "risk_tier"]).agg(
    total_customers=("customer_id", "count"),
    default_rate=("target", "mean"),
    avg_ltv=("ltv_score", "mean")
).round(2).reset_index()
cohort2 = cohort2.sort_values("avg_ltv", ascending=False)
print(cohort2.to_string(index=False))

# ── Cohort 3: Education x Income band ──────────────────────
print("\n── Cohort 3: Education x Income Band ──")
cohort3 = df.groupby(["education_type", "income_band"]).agg(
    total_customers=("customer_id", "count"),
    default_rate=("target", "mean"),
    avg_ltv=("ltv_score", "mean")
).round(2).reset_index()
cohort3 = cohort3.sort_values("avg_ltv", ascending=False)
print(cohort3.to_string(index=False))

# ── Summary ─────────────────────────────────────────────────
best = cohort1.iloc[0]
worst = cohort1.iloc[-1]
print("\n" + "=" * 55)
print("COHORT ANALYSIS COMPLETE")
print(f"  Best segment:  {best.risk_tier} + {best.income_band} → LTV ${best.avg_ltv:,.2f}")
print(f"  Worst segment: {worst.risk_tier} + {worst.income_band} → LTV ${worst.avg_ltv:,.2f}")
print(f"  Total cohorts analysed: {len(cohort1) + len(cohort2) + len(cohort3)}")
print("=" * 55)
