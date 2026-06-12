# Retail Banking Customer Analytics Platform

![Python](https://img.shields.io/badge/Python-3.11-blue)
![AWS](https://img.shields.io/badge/AWS-Glue%20%7C%20S3%20%7C%20Redshift-orange)
![dbt](https://img.shields.io/badge/dbt-2.0-red)
![XGBoost](https://img.shields.io/badge/XGBoost-AUC%200.69-green)
![Power BI](https://img.shields.io/badge/Power%20BI-3%20Pages-yellow)

## Project Overview

End-to-end retail banking analytics platform built on AWS, covering data engineering, analytics, and machine learning. Uses the Home Credit Default Risk dataset (307,511 loan applications) to predict credit defaults, segment customers, and forecast risk trends.

---

## Architecture

Kaggle Dataset (307K records)

│

▼

AWS S3 (Raw Layer)

│

▼

AWS Glue ETL (PySpark) — 5m 57s | 2 DPUs

│

▼

AWS S3 (Cleaned Parquet — 6 tables)

│

▼

Amazon Redshift Serverless

│

├──► dbt (6 models, 9 tests — 15/15 passed)

├──► Apache Airflow (daily 06:00 UTC)

├──► AWS CloudWatch (3 alarms)

├──► Power BI (3 pages, 9 visuals)

└──► ML Layer (XGBoost, Churn, LTV, SARIMA)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Storage | AWS S3 |
| ETL | AWS Glue (PySpark) |
| Warehouse | Amazon Redshift Serverless |
| Transformation | dbt 2.0 |
| Orchestration | Apache Airflow 3.2 |
| Monitoring | AWS CloudWatch + SNS |
| BI Dashboard | Power BI Desktop |
| ML Models | XGBoost, Random Forest, SMOTE |
| Explainability | SHAP |
| Forecasting | SARIMA |
| Statistical Testing | Chi-square, t-test, A/B framework |
| Language | Python 3.11, SQL |

---

## Dataset

**Home Credit Default Risk** — Kaggle
Link: [kaggle.com/c/home-credit-default-risk](https://www.kaggle.com/c/home-credit-default-risk)

| File | Rows |
|---|---|
| application_train.csv | 307,511 |
| bureau.csv | ~1.7M |
| previous_application.csv | ~1.6M |
| installments_payments.csv | ~13.6M |
| credit_card_balance.csv | ~3.8M |
| POS_CASH_balance.csv | ~10M |

---

## Layer 1 — Data Engineering

### AWS Glue ETL
- Reads 7 raw CSVs from S3
- Cleans nulls, standardises column names to snake_case
- Derives 5 new features per table
- Writes cleaned Parquet to S3
- **Execution time: 5m 57s on 2 DPU workers**

### Redshift Star Schema

| Table | Rows |
|---|---|
| fact_loans | 307,511 |
| dim_customers | 307,511 |
| dim_applications | 307,511 |
| dim_date | 3,650 |

### dbt Models

| Model | Type | Purpose |
|---|---|---|
| stg_applications | View | Clean loan applications |
| stg_customers | View | Clean customer data |
| stg_applications_dim | View | Application dimensions |
| mart_loan_performance | Table | Default rates by segment |
| mart_customer_risk | Table | Risk tier classification |
| mart_application_funnel | Table | Funnel metrics |

**dbt build: 15/15 passed — 6 models + 9 tests**

### Airflow DAG

trigger_glue_job → wait_for_glue → run_dbt_build → data_quality_check → notify_success

- Schedule: daily at 06:00 UTC
- Retries: 3 per task

---

## Layer 2 — Data Analytics

### A/B Testing Results

| Test | Statistic | P-value | Result |
|---|---|---|---|
| Cash vs Revolving default rate | χ² = 293.15 | p < 0.0001 | Significant |
| Income: defaulters vs non-defaulters | t = -2.21 | p = 0.027 | Significant |

- Required sample size: **8,572 per group**
- Cash loans default rate: **8.35%** vs Revolving: **5.48%**

### Customer Segmentation

| Segment | Customers | Default Rate | Avg LTV |
|---|---|---|---|
| Low Risk + High Income | 11,292 | 2% | $20,452 |
| Low Risk + Mid Income | 14,129 | 2% | $12,131 |
| Medium Risk + High Income | 35,822 | 4% | $8,741 |
| High Risk + Mid Income | 88,612 | 12% | -$13,896 |

---

## Layer 3 — Data Science

### Model Comparison

| Model | AUC-ROC | Accuracy |
|---|---|---|
| XGBoost (production) | **0.6918** | 0.82 |
| Random Forest | 0.6766 | 0.74 |
| Churn Model | **0.9019** | 0.92 |
| LTV Model | R² = 0.05 | — |
| SARIMA Forecast | MAE = 0.0055 | — |

### SHAP Top 5 Predictors

| Rank | Feature | SHAP Importance |
|---|---|---|
| 1 | ext_source_mean | 0.6526 |
| 2 | payment_rate | 0.4567 |
| 3 | income_type | 0.4533 |
| 4 | employment_years | 0.3600 |
| 5 | age_years | 0.3047 |

### SMOTE Class Balancing
- Before: 91.9% non-default / 8.1% default
- After: 50% / 50%

### What-If Scenario — 20% Income Drop
- Baseline default probability: **26.71%**
- Post income shock: **26.18%**
- Finding: External credit score dominates over income in predicting defaults

---

## Key Business Findings

1. **External credit score is the #1 predictor** — customers with ext_source_mean below 0.35 default at 3× the baseline rate
2. **Cash loans default at 8.35% vs revolving at 5.48%** — statistically significant (p < 0.0001)
3. **Lower secondary education customers default at 11%** vs academic degree holders at 2%
4. **Customers aged 20-30 default at 12%** vs customers over 60 at 4%
5. **High Risk + Mid Income loses $13,896 per customer** — worst LTV segment
6. **Churn model achieves 90% AUC** — reliable early warning system

---

## How to Run

### Setup
```bash
git clone https://github.com/yourusername/Retail-Banking-Customer-Analytics-Platform
cd Retail-Banking-Customer-Analytics-Platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
Create `.env` file:

AWS_ACCESS_KEY_ID=your_key

AWS_SECRET_ACCESS_KEY=your_secret

AWS_REGION=us-east-1

REDSHIFT_HOST=banking-workgroup.608325783808.us-east-1.redshift-serverless.amazonaws.com

REDSHIFT_PORT=5439

REDSHIFT_DB=dev

REDSHIFT_USER=dbadmin

REDSHIFT_PASSWORD=your_password

S3_BUCKET=retail-banking-analytics-prasad

REDSHIFT_IAM_ROLE=arn:aws:iam::608325783808:role/banking-redshift-s3-role

### Run Pipeline
```bash
aws s3 cp data/raw/ s3://retail-banking-analytics-prasad/raw/home-credit/ --recursive
aws glue start-job-run --job-name banking-etl-job
python warehouse/load_to_redshift.py
cd dbt && dbt build
```

### Run ML Models
```bash
python models/credit_risk_xgboost.py
python models/random_forest_credit_risk.py
python models/ltv_churn_models.py
python models/time_series_forecast.py
```

---

## Project Structure
Retail-Banking-Customer-Analytics-Platform/

├── README.md

├── data/raw/                    # gitignored

├── ingestion/

│   └── glue_etl_job.py

├── warehouse/

│   ├── redshift_schema.sql

│   └── load_to_redshift.py

├── dbt/

│   ├── dbt_project.yml

│   └── models/

│       ├── staging/

│       └── marts/

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

└── models/

├── credit_risk_xgboost.py

├── random_forest_credit_risk.py

├── ltv_churn_models.py

├── time_series_forecast.py

└── outputs/

├── xgboost_credit_risk.pkl

├── churn_model.pkl

├── roc_curve.png

├── shap_summary.png

└── sarima_forecast.png


---

## Author

Built by Prasad Patil — portfolio project demonstrating end-to-end data engineering, analytics, and data science in retail banking.

**Skills:** AWS Glue · Redshift · dbt · Airflow · CloudWatch · Power BI · XGBoost · SHAP · SARIMA · A/B Testing · Python · SQL