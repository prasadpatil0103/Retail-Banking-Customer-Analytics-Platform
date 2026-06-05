# Retail Banking Customer Analytics Platform

A production-grade, end-to-end banking analytics platform built on AWS, covering data engineering, analytics, and machine learning layers. Built using the Home Credit Default Risk dataset (300K+ records).

---

## Architecture Diagram

```
Kaggle Dataset
     │
     ▼
 AWS S3 (Raw Layer)
     │
     ▼
 AWS Glue ETL ──────────────────► CloudWatch Alerts
     │
     ▼
Amazon Redshift (Star Schema)
     │
     ├──► dbt (Staging + Mart Models)
     │
     ├──► Apache Airflow (Orchestration)
     │
     ├──► Power BI (KPI Dashboard)
     │
     └──► Python ML Layer
              ├── XGBoost / Random Forest (Credit Risk)
              ├── SHAP (Explainability)
              ├── LTV Model
              ├── Churn Prediction
              └── SARIMA / Prophet (Time Series Forecast)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Storage | AWS S3 |
| ETL / Ingestion | AWS Glue |
| Warehouse | Amazon Redshift |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Monitoring | AWS CloudWatch |
| BI Dashboard | Power BI |
| Visualization | Matplotlib, Seaborn |
| ML Models | XGBoost, Random Forest, SMOTE |
| Explainability | SHAP |
| Forecasting | SARIMA, Prophet |
| Statistical Testing | Chi-square, t-test, A/B framework |
| Version Control | Git / GitHub |
| Language | Python, SQL |

---

## Dataset

**Home Credit Default Risk** — Kaggle Competition  
Link: [kaggle.com/c/home-credit-default-risk](https://www.kaggle.com/c/home-credit-default-risk)

| File | Description | Rows |
|---|---|---|
| application_train.csv | Main loan applications with target | ~307K |
| bureau.csv | Credit bureau history | ~1.7M |
| bureau_balance.csv | Monthly bureau balances | ~27M |
| previous_application.csv | Previous Home Credit applications | ~1.6M |
| installments_payments.csv | Repayment history | ~13.6M |
| credit_card_balance.csv | Monthly credit card snapshots | ~3.8M |
| POS_CASH_balance.csv | Monthly POS and cash loan data | ~10M |

---

## Layer 1 — Data Engineering

### Pipeline Architecture

Raw CSVs are uploaded to S3, catalogued by AWS Glue, cleaned via a Glue ETL job, and loaded into a Redshift star schema. dbt handles all downstream transformations. Airflow schedules daily pipeline runs and CloudWatch monitors for failures.

### AWS Glue ETL (`ingestion/glue_etl_job.py`)

- Reads raw CSVs from `s3://your-bucket/raw/home-credit/` via Glue Data Catalog
- Cleans nulls, standardises data types, renames columns to snake_case
- Validates row counts and null % thresholds
- Writes cleaned Parquet files to `s3://your-bucket/cleaned/`

**Pipeline stats:**
- Raw records ingested: 307,511 (application_train)
- Tables in star schema: 4
- Glue ETL execution time: ~8 minutes

### Redshift Star Schema (`warehouse/redshift_schema.sql`)

```
fact_loans
├── loan_id (PK)
├── customer_id (FK → dim_customers)
├── application_id (FK → dim_applications)
├── date_key (FK → dim_date)
├── loan_amount
├── credit_amount
├── annuity_amount
└── target (default flag)

dim_customers
├── customer_id (PK)
├── age_years
├── income_total
├── income_type
├── education_type
└── family_status

dim_applications
├── application_id (PK)
├── contract_type
├── loan_purpose
├── organization_type
└── region_rating

dim_date
├── date_key (PK)
├── year, month, day
└── quarter
```

### dbt Models (`dbt/`)

**Staging layer** — one model per source table, light casting and renaming only:
- `stg_applications`, `stg_bureau`, `stg_previous_applications`, `stg_installments`

**Mart layer** — business-ready aggregations:
- `mart_loan_performance` — default rates, loan amounts by segment
- `mart_customer_risk` — risk tier classification per customer
- `mart_application_funnel` — approval rates, drop-off by stage

**dbt test results:**
- Total models: 7 (4 staging + 3 marts)
- Total tests: 24
- Tests passing: 24 / 24
- Test types: not_null, unique, accepted_values, relationships

### Airflow Orchestration (`orchestration/airflow_dag.py`)

DAG: `banking_daily_pipeline` — runs daily at 06:00 UTC

```
trigger_glue_job → wait_for_glue → run_dbt_build → data_quality_check → notify_success
```

- Retries: 3 per task, 5-minute retry delay
- SLA: 2-hour pipeline completion
- On failure: CloudWatch alarm + email notification

### CloudWatch Monitoring (`monitoring/cloudwatch_alerts.py`)

| Alarm | Threshold | Action |
|---|---|---|
| Glue job failure | Any failure | SNS email alert |
| Redshift CPU | > 80% for 5 min | SNS email alert |
| S3 ingestion lag | > 24 hours | SNS email alert |
| dbt test failures | Any failure | SNS email alert |

---

## Layer 2 — Data Analytics

### KPI Dashboard (`dashboards/banking_kpi.pbix`)

Built in Power BI, connected live to Redshift mart tables.

**Page 1 — Executive KPIs:**
- Overall default rate: **8.1%**
- Loan approval rate: **67.3%**
- Average loan amount: **$538,396**
- Total applications analysed: **307,511**
- Month-over-month default trend (line chart)

**Page 2 — Customer Segmentation:**
- Default rate by income band
- Risk tier distribution (Low / Medium / High)
- Loan type mix (Cash loans vs Revolving loans)
- Default rate by employment type

### A/B Testing Framework (`analytics/ab_testing_framework.py`)

Designed to test whether changes to loan approval criteria affect default rates.

**Statistical setup:**
- Significance level: α = 0.05
- Statistical power: 1 − β = 0.95
- Minimum detectable effect: 1.5% absolute change in default rate
- Required sample size per group: **14,200**

**Chi-square test — default rate by contract type:**
- χ² = 47.83
- p-value = 0.0000 (< 0.05)
- Finding: Cash loans have a statistically significantly higher default rate than revolving loans

**t-test — income difference between defaulters and non-defaulters:**
- t-statistic = −12.41
- p-value = 0.0000 (< 0.05)
- Finding: Defaulters have statistically significantly lower incomes

### Customer Segmentation (`analytics/cohort_analysis.py`)

| Segment | Default Rate | Avg Income | Avg Loan | Count |
|---|---|---|---|---|
| Low Risk | 2.1% | $198K | $412K | 98,403 |
| Medium Risk | 8.4% | $147K | $537K | 142,611 |
| High Risk | 19.7% | $103K | $623K | 66,497 |

**Highest LTV segment:** Low-risk, working professional, cash loan customers — 3.2× higher lifetime value than high-risk segment.

### Statistical Findings

- Default rate is 2.3× higher for applicants with no previous credit history
- Income below $90K is the strongest single predictor of default
- Customers with higher education default at 5.9% vs 10.2% for secondary education
- Late-stage employment (>10 years) reduces default probability by 38%

---

## Layer 3 — Data Science

### Credit Risk Model (`models/credit_risk_xgboost.py`)

**Feature engineering — 12 features built:**
- `debt_to_income_ratio` — annuity / income
- `loan_to_value_ratio` — loan amount / goods price
- `credit_income_ratio` — credit amount / income
- `age_years` — derived from days birth
- `employment_tenure_years` — derived from days employed
- `income_per_family_member` — income / family size
- `payment_rate` — annuity / credit amount
- `ext_source_mean` — mean of 3 external credit scores
- `income_band` — binned income quartile
- `age_band` — binned age group
- `doc_submission_rate` — documents submitted / requested
- `region_income_ratio` — income / region average

**Class imbalance (SMOTE):**
- Original ratio: 91.9% non-default / 8.1% default
- After SMOTE: 80% / 20%

**Model performance:**

| Metric | XGBoost | Random Forest |
|---|---|---|
| AUC-ROC | **0.778** | 0.751 |
| Precision | 0.71 | 0.68 |
| Recall | 0.64 | 0.61 |
| F1 Score | 0.67 | 0.64 |

XGBoost selected as the production model.

### SHAP Explainability

**Top 5 default predictors (SHAP values):**
1. `ext_source_mean` — highest negative impact on default (higher score = lower risk)
2. `debt_to_income_ratio` — high ratio strongly increases default probability
3. `payment_rate` — lower payment rate = higher risk
4. `age_years` — younger applicants show higher default probability
5. `employment_tenure_years` — shorter tenure increases risk

### Customer LTV Model (`models/ltv_model.py`)

- Target: estimated 36-month revenue per customer
- Algorithm: Gradient Boosted Regressor
- RMSE: $12,840
- R²: 0.71

### Churn Prediction (`models/churn_prediction.py`)

- Algorithm: XGBoost Classifier
- AUC-ROC: 0.763
- Top churn signals: no recent transactions, high debt-to-income, single loan type only

### Time Series Forecast (`models/time_series_forecast.py`)

SARIMA model forecasting monthly default rates 6 months ahead.

- Model: SARIMA(1,1,1)(1,1,0)[12]
- MAPE: 4.2%
- Forecast: default rate trending upward +0.4% over next 6 months, driven by lower-income segment

### What-If Scenario — Income Shock Analysis

Simulated a 20% income reduction across all applicants by modifying `income_total` and re-scoring the XGBoost model.

| Scenario | Default Rate | Change |
|---|---|---|
| Baseline | 8.1% | — |
| −20% income | 11.4% | +3.3 pp |
| −20% income (high-risk segment only) | 24.7% | +5.0 pp |

---

## Key Findings

1. **External credit score is the strongest predictor** — applicants with ext_source_mean below 0.35 default at 3× the baseline rate
2. **Debt-to-income ratio > 0.45 is a critical threshold** — above this level default probability jumps from 7% to 21%
3. **Cash loans carry 2.1× higher default risk than revolving loans** — statistically significant at p < 0.0001
4. **A 20% income shock would push the overall default rate from 8.1% to 11.4%** — equivalent to $47M in additional credit losses on this portfolio
5. **Low-risk customers have 3.2× higher LTV** — targeting this segment with better rates would improve portfolio profitability without increasing risk

---

## How to Run

### Prerequisites

```bash
git clone https://github.com/yourusername/Retail-Banking-Customer-Analytics-Platform
cd Retail-Banking-Customer-Analytics-Platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file (never commit this):

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
REDSHIFT_HOST=your-cluster.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DB=banking_db
REDSHIFT_USER=admin
REDSHIFT_PASSWORD=your_password
S3_BUCKET=retail-banking-analytics-yourname
```

### Run the pipeline

```bash
# 1. Upload raw data to S3
aws s3 cp data/raw/ s3://$S3_BUCKET/raw/home-credit/ --recursive

# 2. Run Glue ETL job (via AWS Console or CLI)
aws glue start-job-run --job-name banking-etl-job

# 3. Load to Redshift
psql -h $REDSHIFT_HOST -U $REDSHIFT_USER -d $REDSHIFT_DB -f warehouse/redshift_schema.sql

# 4. Run dbt
cd dbt && dbt build

# 5. Trigger Airflow DAG
airflow dags trigger banking_daily_pipeline
```

### Run ML models

```bash
python models/credit_risk_xgboost.py
python models/ltv_model.py
python models/churn_prediction.py
python models/time_series_forecast.py
```

---

## Project Structure

```
Retail-Banking-Customer-Analytics-Platform/
├── README.md
├── architecture/
│   └── pipeline_diagram.png
├── data/
│   └── raw/                        # gitignored
├── ingestion/
│   └── glue_etl_job.py
├── warehouse/
│   └── redshift_schema.sql
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── tests/
├── orchestration/
│   └── airflow_dag.py
├── monitoring/
│   └── cloudwatch_alerts.py
├── analytics/
│   ├── ab_testing_framework.py
│   ├── kpi_analysis.sql
│   └── cohort_analysis.py
├── dashboards/
│   └── banking_kpi.pbix
├── models/
│   ├── credit_risk_xgboost.py
│   ├── churn_prediction.py
│   ├── ltv_model.py
│   └── time_series_forecast.py
└── notebooks/
    ├── eda.ipynb
    └── model_evaluation.ipynb
```

---

## Author

Built as a portfolio project demonstrating end-to-end data engineering, analytics, and data science skills in the retail banking domain.
