
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import warnings
warnings.filterwarnings("ignore")
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import LabelEncoder

print("Loading data...")
df = pd.read_csv("data/raw/application_train.csv")

# ── Build monthly default rate time series ──────────────────
print("Building time series...")
df["age_years"] = (df["DAYS_BIRTH"].abs() / 365).astype(int)
monthly = df.groupby("age_years")["TARGET"].agg(
    default_rate="mean",
    total_loans="count"
).reset_index()
monthly = monthly[monthly["total_loans"] >= 100].sort_values("age_years")
print(f"Time series length: {len(monthly)} periods")

# ── Train/test split ────────────────────────────────────────
train_size = int(len(monthly) * 0.8)
train = monthly["default_rate"].iloc[:train_size]
test  = monthly["default_rate"].iloc[train_size:]

# ── SARIMA model ────────────────────────────────────────────
print("Training SARIMA model...")
model = SARIMAX(train, order=(1,1,1), seasonal_order=(0,1,0,12),
                enforce_stationarity=False, enforce_invertibility=False)
results = model.fit(disp=False)
forecast = results.forecast(steps=len(test))

# Use MAE instead of MAPE to avoid division by zero issues
mae = np.mean(np.abs(test.values - forecast.values))
print(f"SARIMA MAE: {mae:.6f}")
print(f"Forecast (next 5): {forecast.values[:5].round(4)}")

# Save forecast plot
plt.figure(figsize=(10, 5))
plt.plot(monthly["age_years"].iloc[:train_size], train.values, label="Historical", color="blue")
plt.plot(monthly["age_years"].iloc[train_size:], test.values, label="Actual", color="green")
plt.plot(monthly["age_years"].iloc[train_size:], forecast.values, label="Forecast", color="red", linestyle="--")
plt.xlabel("Age (years)")
plt.ylabel("Default Rate")
plt.title("SARIMA Forecast — Default Rate by Age")
plt.legend()
plt.savefig("models/outputs/sarima_forecast.png", dpi=150, bbox_inches="tight")
plt.close()
print("Forecast plot saved")

# ── What-if scenario ────────────────────────────────────────
print("\n── What-If Scenario: 20% Income Drop ──")

df2 = pd.read_csv("data/raw/application_train.csv")
df2 = df2.rename(columns={
    "TARGET": "target", "AMT_CREDIT": "credit_amount",
    "AMT_ANNUITY": "annuity_amount", "AMT_INCOME_TOTAL": "income_total",
    "NAME_CONTRACT_TYPE": "contract_type", "NAME_INCOME_TYPE": "income_type",
    "NAME_EDUCATION_TYPE": "education_type", "DAYS_BIRTH": "days_birth",
    "DAYS_EMPLOYED": "days_employed", "REGION_RATING_CLIENT": "region_rating",
    "EXT_SOURCE_1": "ext_source_1", "EXT_SOURCE_2": "ext_source_2",
    "EXT_SOURCE_3": "ext_source_3",
})

df2["age_years"]            = (df2["days_birth"].abs() / 365).astype(int)
df2["employment_years"]     = df2["days_employed"].apply(lambda x: 0 if x > 0 else int(abs(x)/365))
df2["debt_to_income_ratio"] = (df2["annuity_amount"] / df2["income_total"]).round(4)
df2["credit_income_ratio"]  = (df2["credit_amount"] / df2["income_total"]).round(4)
df2["ext_source_mean"]      = df2[["ext_source_1","ext_source_2","ext_source_3"]].fillna(0).mean(axis=1).round(4)
df2["payment_rate"]         = (df2["annuity_amount"] / df2["credit_amount"]).round(4)
df2["loan_to_income"]       = (df2["credit_amount"] / df2["income_total"]).round(4)
df2["income_per_person"]    = (df2["income_total"] / df2["age_years"]).round(2)
df2["credit_per_age"]       = (df2["credit_amount"] / df2["age_years"]).round(2)
df2["dti_age_interaction"]  = (df2["debt_to_income_ratio"] * df2["age_years"]).round(4)

le = LabelEncoder()
for col in ["contract_type", "income_type", "education_type"]:
    df2[col + "_enc"] = le.fit_transform(df2[col].astype(str))

features = [
    "credit_amount", "annuity_amount", "income_total",
    "debt_to_income_ratio", "credit_income_ratio", "ext_source_mean",
    "age_years", "employment_years", "region_rating",
    "payment_rate", "loan_to_income", "income_per_person",
    "credit_per_age", "dti_age_interaction",
    "contract_type_enc", "income_type_enc", "education_type_enc"
]

df_clean = df2[features + ["target"]].dropna()
X_base = df_clean[features]

with open("models/outputs/xgboost_credit_risk.pkl", "rb") as f:
    xgb_model = pickle.load(f)

baseline_rate = xgb_model.predict_proba(X_base)[:, 1].mean()

df_shock = df_clean.copy()
df_shock["income_total"]       = df_shock["income_total"] * 0.8
df_shock["debt_to_income_ratio"] = (df_shock["annuity_amount"] / df_shock["income_total"]).round(4)
df_shock["credit_income_ratio"]  = (df_shock["credit_amount"] / df_shock["income_total"]).round(4)
df_shock["loan_to_income"]       = (df_shock["credit_amount"] / df_shock["income_total"]).round(4)
df_shock["income_per_person"]    = (df_shock["income_total"] / df_shock["age_years"]).round(2)

shock_rate = xgb_model.predict_proba(df_shock[features])[:, 1].mean()

print(f"Baseline default probability:  {baseline_rate:.4f} ({baseline_rate*100:.2f}%)")
print(f"After 20% income shock:        {shock_rate:.4f} ({shock_rate*100:.2f}%)")
print(f"Change:                        +{(shock_rate-baseline_rate)*100:.2f} percentage points")

print("\n" + "=" * 55)
print("TIME SERIES + WHAT-IF COMPLETE")
print(f"  SARIMA MAE:           {mae:.6f}")
print(f"  Baseline default:     {baseline_rate*100:.2f}%")
print(f"  Post income shock:    {shock_rate*100:.2f}%")
print(f"  Impact:               +{(shock_rate-baseline_rate)*100:.2f} pp")
print("=" * 55)
