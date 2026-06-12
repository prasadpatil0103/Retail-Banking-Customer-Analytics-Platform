
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.power import TTestIndPower, NormalIndPower
from statsmodels.stats.proportion import proportions_ztest
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# ── Connect to Redshift ─────────────────────────────────────
conn = psycopg2.connect(
    host=os.getenv("REDSHIFT_HOST"),
    port=os.getenv("REDSHIFT_PORT"),
    dbname=os.getenv("REDSHIFT_DB"),
    user=os.getenv("REDSHIFT_USER"),
    password=os.getenv("REDSHIFT_PASSWORD"),
    sslmode="require"
)
print("Connected to Redshift")

# ── Load data ───────────────────────────────────────────────
query = """
    SELECT
        customer_id,
        contract_type,
        income_type,
        education_type,
        income_total,
        credit_amount,
        debt_to_income_ratio,
        ext_source_mean,
        age_years,
        employment_years,
        region_rating,
        target
    FROM fact_loans
"""
df = pd.read_sql(query, conn)
conn.close()
print(f"Loaded {len(df):,} rows from Redshift")

# ════════════════════════════════════════════════════════════
# PART 1 — Sample Size Calculation
# ════════════════════════════════════════════════════════════
print("\n── Part 1: Sample Size Calculation ──")

baseline_rate    = df["target"].mean()
min_effect       = 0.015
alpha            = 0.05
power            = 0.95

analysis = NormalIndPower()
sample_size = analysis.solve_power(
    effect_size=min_effect / np.sqrt(baseline_rate * (1 - baseline_rate)),
    alpha=alpha,
    power=power,
    alternative="two-sided"
)

print(f"Baseline default rate:        {baseline_rate:.2%}")
print(f"Minimum detectable effect:    {min_effect:.2%}")
print(f"Significance level (alpha):   {alpha}")
print(f"Statistical power:            {power}")
print(f"Required sample size/group:   {int(sample_size):,}")

# ════════════════════════════════════════════════════════════
# PART 2 — A/B Test: Cash Loans vs Revolving Loans
# ════════════════════════════════════════════════════════════
print("\n── Part 2: Chi-Square Test — Contract Type vs Default ──")

control   = df[df["contract_type"] == "Cash loans"]["target"]
treatment = df[df["contract_type"] == "Revolving loans"]["target"]

print(f"Control group (Cash loans):      {len(control):,} customers, default rate: {control.mean():.2%}")
print(f"Treatment group (Revolving):     {len(treatment):,} customers, default rate: {treatment.mean():.2%}")

contingency = pd.crosstab(df["contract_type"], df["target"])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"Chi-square statistic:            {chi2:.4f}")
print(f"Degrees of freedom:              {dof}")
print(f"P-value:                         {p_value:.6f}")
print(f"Statistically significant:       {'YES' if p_value < alpha else 'NO'}")

effect_size = np.sqrt(chi2 / len(df))
print(f"Effect size (Cramer V):          {effect_size:.4f}")

# ════════════════════════════════════════════════════════════
# PART 3 — T-Test: Income difference between defaulters
# ════════════════════════════════════════════════════════════
print("\n── Part 3: T-Test — Income vs Default ──")

defaulters     = df[df["target"] == 1]["income_total"]
non_defaulters = df[df["target"] == 0]["income_total"]

t_stat, t_pvalue = stats.ttest_ind(defaulters, non_defaulters)

print(f"Defaulters avg income:           ${defaulters.mean():,.0f}")
print(f"Non-defaulters avg income:       ${non_defaulters.mean():,.0f}")
print(f"T-statistic:                     {t_stat:.4f}")
print(f"P-value:                         {t_pvalue:.6f}")
print(f"Statistically significant:       {'YES' if t_pvalue < alpha else 'NO'}")

ci = stats.t.interval(
    0.95,
    df=len(defaulters)-1,
    loc=defaulters.mean(),
    scale=stats.sem(defaulters)
)
print(f"95% CI for defaulter income:     (${ci[0]:,.0f}, ${ci[1]:,.0f})")

# ════════════════════════════════════════════════════════════
# PART 4 — Customer Segmentation
# ════════════════════════════════════════════════════════════
print("\n── Part 4: Customer Segmentation ──")

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

segmentation = df.groupby(["risk_tier", "income_band"]).agg(
    total_customers=("customer_id", "count"),
    default_rate=("target", "mean"),
    avg_income=("income_total", "mean"),
    avg_credit=("credit_amount", "mean")
).round(4).reset_index()

print(segmentation.to_string(index=False))

# ════════════════════════════════════════════════════════════
# PART 5 — Cohort Retention Analysis
# ════════════════════════════════════════════════════════════
print("\n── Part 5: Cohort LTV Analysis ──")

df["ltv_score"] = (
    (1 - df["target"]) * df["credit_amount"] * 0.03
    - df["target"] * df["credit_amount"] * 0.45
)

cohort_ltv = df.groupby(["risk_tier", "income_band"]).agg(
    avg_ltv=("ltv_score", "mean"),
    total_customers=("customer_id", "count")
).round(2).reset_index()

cohort_ltv = cohort_ltv.sort_values("avg_ltv", ascending=False)
print(cohort_ltv.to_string(index=False))

# ════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("A/B TESTING FRAMEWORK COMPLETE")
print(f"  Chi-square: {chi2:.2f}, p-value: {p_value:.6f}")
print(f"  T-statistic: {t_stat:.2f}, p-value: {t_pvalue:.6f}")
print(f"  Required sample size: {int(sample_size):,} per group")
print(f"  Customer segments analysed: {len(segmentation)}")
print("=" * 55)
