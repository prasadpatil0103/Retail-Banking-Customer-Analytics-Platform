
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, roc_auc_score, roc_curve)
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import shap
import pickle
import warnings
warnings.filterwarnings("ignore")

# ── Load data from local CSV ────────────────────────────────
print("Loading data from local CSV...")
df = pd.read_csv("data/raw/application_train.csv")
print(f"Loaded {len(df):,} rows, {len(df.columns)} columns")

# ── Rename key columns ──────────────────────────────────────
df = df.rename(columns={
    "SK_ID_CURR":          "customer_id",
    "TARGET":              "target",
    "AMT_CREDIT":          "credit_amount",
    "AMT_ANNUITY":         "annuity_amount",
    "AMT_INCOME_TOTAL":    "income_total",
    "AMT_GOODS_PRICE":     "goods_price",
    "NAME_CONTRACT_TYPE":  "contract_type",
    "NAME_INCOME_TYPE":    "income_type",
    "NAME_EDUCATION_TYPE": "education_type",
    "DAYS_BIRTH":          "days_birth",
    "DAYS_EMPLOYED":       "days_employed",
    "REGION_RATING_CLIENT":"region_rating",
    "EXT_SOURCE_1":        "ext_source_1",
    "EXT_SOURCE_2":        "ext_source_2",
    "EXT_SOURCE_3":        "ext_source_3",
    "CNT_FAM_MEMBERS":     "family_members",
})

# ── Feature engineering ─────────────────────────────────────
print("Engineering features...")
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

# Encode categoricals
le = LabelEncoder()
for col in ["contract_type", "income_type", "education_type"]:
    df[col + "_enc"] = le.fit_transform(df[col].astype(str))

# ── Define features ─────────────────────────────────────────
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

print(f"Features: {len(features)}")
print(f"Rows after dropna: {len(df_model):,}")
print(f"Class distribution before SMOTE: {y.value_counts().to_dict()}")

# ── Train/test split ────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── SMOTE ───────────────────────────────────────────────────
print("\nApplying SMOTE...")
smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
print(f"Before SMOTE: {pd.Series(y_train).value_counts().to_dict()}")
print(f"After SMOTE:  {pd.Series(y_train_sm).value_counts().to_dict()}")

# ── XGBoost model ───────────────────────────────────────────
print("\nTraining XGBoost model...")
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="auc",
    random_state=42
)
xgb_model.fit(X_train_sm, y_train_sm)

# ── Evaluate ────────────────────────────────────────────────
y_pred = xgb_model.predict(X_test)
y_prob = xgb_model.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)
print(f"\n── XGBoost Results ──")
print(f"AUC-ROC: {auc:.4f}")
print(classification_report(y_test, y_pred))

# ── SHAP explainability ─────────────────────────────────────
print("\nCalculating SHAP values...")
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test[:500])

print("\n── Top 10 SHAP Feature Importances ──")
shap_importance = pd.DataFrame({
    "feature":    features,
    "importance": np.abs(shap_values).mean(axis=0)
}).sort_values("importance", ascending=False)
print(shap_importance.head(10).to_string(index=False))

# ── Save outputs ────────────────────────────────────────────
os.makedirs("models/outputs", exist_ok=True)

# ROC curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"AUC = {auc:.4f}")
plt.plot([0, 1], [0, 1], color="navy", linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("XGBoost ROC Curve — Credit Risk Model")
plt.legend(loc="lower right")
plt.savefig("models/outputs/roc_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nROC curve saved")

# SHAP summary plot
plt.figure()
shap.summary_plot(shap_values, X_test[:500], feature_names=features, show=False)
plt.savefig("models/outputs/shap_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print("SHAP summary saved")

# Save model
with open("models/outputs/xgboost_credit_risk.pkl", "wb") as f:
    pickle.dump(xgb_model, f)
print("Model saved")

print("\n" + "=" * 55)
print("CREDIT RISK MODEL COMPLETE")
print(f"  AUC-ROC:             {auc:.4f}")
print(f"  Features engineered: {len(features)}")
print(f"  Top predictor:       {shap_importance.iloc[0].feature}")
print(f"  SMOTE ratio:         {pd.Series(y_train_sm).value_counts().to_dict()}")
print("=" * 55)
