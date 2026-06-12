
import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings("ignore")
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

print("Loading data...")
df = pd.read_csv("data/raw/application_train.csv")

df = df.rename(columns={
    "SK_ID_CURR": "customer_id", "TARGET": "target",
    "AMT_CREDIT": "credit_amount", "AMT_ANNUITY": "annuity_amount",
    "AMT_INCOME_TOTAL": "income_total", "NAME_CONTRACT_TYPE": "contract_type",
    "NAME_INCOME_TYPE": "income_type", "NAME_EDUCATION_TYPE": "education_type",
    "DAYS_BIRTH": "days_birth", "DAYS_EMPLOYED": "days_employed",
    "REGION_RATING_CLIENT": "region_rating",
    "EXT_SOURCE_1": "ext_source_1", "EXT_SOURCE_2": "ext_source_2",
    "EXT_SOURCE_3": "ext_source_3",
})

df["age_years"]            = (df["days_birth"].abs() / 365).astype(int)
df["employment_years"]     = df["days_employed"].apply(lambda x: 0 if x > 0 else int(abs(x)/365))
df["debt_to_income_ratio"] = (df["annuity_amount"] / df["income_total"]).round(4)
df["ext_source_mean"]      = df[["ext_source_1","ext_source_2","ext_source_3"]].fillna(0).mean(axis=1).round(4)
df["payment_rate"]         = (df["annuity_amount"] / df["credit_amount"]).round(4)
df["loan_to_income"]       = (df["credit_amount"] / df["income_total"]).round(4)

le = LabelEncoder()
for col in ["contract_type", "income_type", "education_type"]:
    df[col + "_enc"] = le.fit_transform(df[col].astype(str))

features = [
    "credit_amount", "annuity_amount", "income_total",
    "debt_to_income_ratio", "ext_source_mean", "age_years",
    "employment_years", "region_rating", "payment_rate", "loan_to_income",
    "contract_type_enc", "income_type_enc", "education_type_enc"
]

df_model = df[features + ["target"]].dropna()
X = df_model[features]
y = df_model["target"]

# ════════════════════════════════════════════════════════════
# LTV MODEL
# ════════════════════════════════════════════════════════════
print("\n── Building LTV Model ──")

df_model["ltv"] = (
    (1 - df_model["target"]) * df_model["credit_amount"] * 0.03
    - df_model["target"] * df_model["credit_amount"] * 0.45
)

X_ltv = df_model[features]
y_ltv = df_model["ltv"]

X_train_ltv, X_test_ltv, y_train_ltv, y_test_ltv = train_test_split(
    X_ltv, y_ltv, test_size=0.2, random_state=42
)

ltv_model = GradientBoostingRegressor(
    n_estimators=100, max_depth=5,
    learning_rate=0.1, random_state=42
)
ltv_model.fit(X_train_ltv, y_train_ltv)

y_pred_ltv = ltv_model.predict(X_test_ltv)
rmse = np.sqrt(mean_squared_error(y_test_ltv, y_pred_ltv))
r2   = r2_score(y_test_ltv, y_pred_ltv)

print(f"LTV Model RMSE: ${rmse:,.2f}")
print(f"LTV Model R²:   {r2:.4f}")

with open("models/outputs/ltv_model.pkl", "wb") as f:
    pickle.dump(ltv_model, f)
print("LTV model saved")

# ════════════════════════════════════════════════════════════
# CHURN MODEL
# ════════════════════════════════════════════════════════════
print("\n── Building Churn Model ──")

df_model["churn"] = (
    (df_model["target"] == 1) |
    (df_model["payment_rate"] < 0.02) |
    (df_model["ext_source_mean"] < 0.2)
).astype(int)

X_churn = df_model[features]
y_churn = df_model["churn"]

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_churn, y_churn, test_size=0.2, random_state=42, stratify=y_churn
)

smote = SMOTE(random_state=42)
X_train_c_sm, y_train_c_sm = smote.fit_resample(X_train_c, y_train_c)

churn_model = GradientBoostingClassifier(
    n_estimators=100, max_depth=5,
    learning_rate=0.1, random_state=42
)
churn_model.fit(X_train_c_sm, y_train_c_sm)

y_pred_c = churn_model.predict(X_test_c)
y_prob_c = churn_model.predict_proba(X_test_c)[:, 1]
churn_auc = roc_auc_score(y_test_c, y_prob_c)

print(f"Churn Model AUC-ROC: {churn_auc:.4f}")
print(classification_report(y_test_c, y_pred_c))

with open("models/outputs/churn_model.pkl", "wb") as f:
    pickle.dump(churn_model, f)
print("Churn model saved")

print("\n" + "=" * 55)
print("LTV + CHURN MODELS COMPLETE")
print(f"  LTV RMSE:        ${rmse:,.2f}")
print(f"  LTV R²:          {r2:.4f}")
print(f"  Churn AUC-ROC:   {churn_auc:.4f}")
print("=" * 55)
