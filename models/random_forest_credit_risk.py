
import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings("ignore")
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
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
df["credit_income_ratio"]  = (df["credit_amount"] / df["income_total"]).round(4)
df["ext_source_mean"]      = df[["ext_source_1","ext_source_2","ext_source_3"]].fillna(0).mean(axis=1).round(4)
df["payment_rate"]         = (df["annuity_amount"] / df["credit_amount"]).round(4)
df["loan_to_income"]       = (df["credit_amount"] / df["income_total"]).round(4)
df["income_per_person"]    = (df["income_total"] / df["age_years"]).round(2)
df["credit_per_age"]       = (df["credit_amount"] / df["age_years"]).round(2)
df["dti_age_interaction"]  = (df["debt_to_income_ratio"] * df["age_years"]).round(4)

le = LabelEncoder()
for col in ["contract_type", "income_type", "education_type"]:
    df[col + "_enc"] = le.fit_transform(df[col].astype(str))

features = [
    "credit_amount", "annuity_amount", "income_total",
    "debt_to_income_ratio", "credit_income_ratio", "ext_source_mean",
    "age_years", "employment_years", "region_rating",
    "payment_rate", "loan_to_income", "income_per_person",
    "credit_per_age", "dti_age_interaction",
    "contract_type_enc", "income_type_enc", "education_type_enc"
]

df_model = df[features + ["target"]].dropna()
X = df_model[features]
y = df_model["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Applying SMOTE...")
smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

print("Training Random Forest model...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_sm, y_train_sm)

y_pred = rf_model.predict(X_test)
y_prob = rf_model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_prob)

print(f"\n── Random Forest Results ──")
print(f"AUC-ROC: {auc:.4f}")
print(classification_report(y_test, y_pred))

with open("models/outputs/random_forest_credit_risk.pkl", "wb") as f:
    pickle.dump(rf_model, f)
print("Model saved")

print("\n" + "=" * 55)
print("MODEL COMPARISON")
print(f"  XGBoost AUC:       0.6918")
print(f"  Random Forest AUC: {auc:.4f}")
print(f"  Winner: {'XGBoost' if 0.6918 > auc else 'Random Forest'}")
print("=" * 55)
