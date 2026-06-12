import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("REDSHIFT_HOST"),
    port=os.getenv("REDSHIFT_PORT"),
    dbname=os.getenv("REDSHIFT_DB"),
    user=os.getenv("REDSHIFT_USER"),
    password=os.getenv("REDSHIFT_PASSWORD"),
    sslmode="require"
)
conn.autocommit = True
cursor = conn.cursor()
print("Connected to Redshift successfully")

# ── Step 1: Create star schema ──────────────────────────────
print("Creating star schema tables...")
with open("warehouse/redshift_schema.sql", "r") as f:
    sql = f.read()
cursor.execute(sql)
print("Star schema created successfully")

# ── Step 2: Load dim_date ───────────────────────────────────
print("Loading dim_date...")
start_date = date(2015, 1, 1)
rows = []
for i in range(3650):
    d = start_date + timedelta(days=i)
    rows.append(f"({int(d.strftime('%Y%m%d'))}, '{d.strftime('%Y-%m-%d')}', {d.year}, {(d.month-1)//3+1}, {d.month}, '{d.strftime('%B')}', {d.day}, '{d.strftime('%A')}')")

chunk_size = 500
for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i+chunk_size]
    values = ",".join(chunk)
    cursor.execute(f"""
        INSERT INTO dim_date (date_key, full_date, year, quarter, month, month_name, day, day_of_week)
        VALUES {values}
    """)
print("dim_date loaded — 10 years of dates")

# ── Step 3: Read CSV directly ───────────────────────────────
print("Reading application_train.csv...")
df = pd.read_csv("data/raw/application_train.csv")
print(f"Loaded {len(df):,} rows from CSV")

# Rename columns to match our schema
df = df.rename(columns={
    "SK_ID_CURR":         "customer_id",
    "TARGET":             "target",
    "NAME_CONTRACT_TYPE": "contract_type",
    "AMT_CREDIT":         "credit_amount",
    "AMT_ANNUITY":        "annuity_amount",
    "AMT_INCOME_TOTAL":   "income_total",
    "AMT_GOODS_PRICE":    "goods_price",
    "NAME_INCOME_TYPE":   "income_type",
    "NAME_EDUCATION_TYPE":"education_type",
    "NAME_FAMILY_STATUS": "family_status",
    "DAYS_BIRTH":         "days_birth",
    "DAYS_EMPLOYED":      "days_employed",
    "CNT_FAM_MEMBERS":    "family_members",
    "REGION_RATING_CLIENT":"region_rating",
    "EXT_SOURCE_1":       "ext_source_1",
    "EXT_SOURCE_2":       "ext_source_2",
    "EXT_SOURCE_3":       "ext_source_3"
})

# Derive columns
import numpy as np
df["age_years"]            = (df["days_birth"].abs() / 365).astype(int)
df["employment_years"]     = df["days_employed"].apply(lambda x: 0 if x > 0 else int(abs(x)/365))
df["debt_to_income_ratio"] = (df["annuity_amount"] / df["income_total"]).round(4)
df["credit_income_ratio"]  = (df["credit_amount"] / df["income_total"]).round(4)
df["ext_source_mean"]      = df[["ext_source_1","ext_source_2","ext_source_3"]].fillna(0).mean(axis=1).round(4)
df["ingestion_timestamp"]  = pd.Timestamp.utcnow()

# ── Step 4: Load dim_customers ──────────────────────────────
print("Loading dim_customers...")
dim_customers = df[[
    "customer_id","age_years","income_total","income_type",
    "education_type","family_status","family_members",
    "employment_years","region_rating"
]].drop_duplicates(subset=["customer_id"])

chunk_size = 1000
for i in range(0, len(dim_customers), chunk_size):
    chunk = dim_customers.iloc[i:i+chunk_size]
    rows = []
    for _, row in chunk.iterrows():
        family = "NULL" if pd.isna(row["family_members"]) else row["family_members"]
        rows.append(f"({row['customer_id']}, {row['age_years']}, {row['income_total']}, $${row['income_type']}$$, $${row['education_type']}$$, $${row['family_status']}$$, {family}, {row['employment_years']}, {row['region_rating']})")
    cursor.execute(f"INSERT INTO dim_customers VALUES {','.join(rows)}")
    if i % 10000 == 0:
        print(f"  dim_customers: {i:,} / {len(dim_customers):,}")
print("dim_customers loaded")

# ── Step 5: Load dim_applications ──────────────────────────
print("Loading dim_applications...")
dim_applications = df[[
    "customer_id","contract_type","credit_amount","annuity_amount",
    "goods_price","ext_source_1","ext_source_2","ext_source_3","ext_source_mean"
]].drop_duplicates(subset=["customer_id"])

for i in range(0, len(dim_applications), chunk_size):
    chunk = dim_applications.iloc[i:i+chunk_size]
    rows = []
    for _, row in chunk.iterrows():
        goods  = "NULL" if pd.isna(row["goods_price"]) else row["goods_price"]
        es1    = "NULL" if pd.isna(row["ext_source_1"]) else row["ext_source_1"]
        es2    = "NULL" if pd.isna(row["ext_source_2"]) else row["ext_source_2"]
        es3    = "NULL" if pd.isna(row["ext_source_3"]) else row["ext_source_3"]
        ann    = "NULL" if pd.isna(row["annuity_amount"]) else row["annuity_amount"]
        rows.append(f"({row['customer_id']}, $${row['contract_type']}$$, {row['credit_amount']}, {ann}, {goods}, {es1}, {es2}, {es3}, {row['ext_source_mean']})")
    cursor.execute(f"INSERT INTO dim_applications VALUES {','.join(rows)}")
    if i % 10000 == 0:
        print(f"  dim_applications: {i:,} / {len(dim_applications):,}")
print("dim_applications loaded")

# ── Step 6: Load fact_loans ─────────────────────────────────
print("Loading fact_loans...")
fact = df[[
    "customer_id","target","credit_amount","annuity_amount",
    "income_total","goods_price","debt_to_income_ratio","credit_income_ratio",
    "ext_source_mean","contract_type","income_type","education_type",
    "region_rating","age_years","employment_years","ingestion_timestamp"
]]

for i in range(0, len(fact), chunk_size):
    chunk = fact.iloc[i:i+chunk_size]
    rows = []
    for _, row in chunk.iterrows():
        goods  = "NULL" if pd.isna(row["goods_price"]) else row["goods_price"]
        dti    = "NULL" if pd.isna(row["debt_to_income_ratio"]) else row["debt_to_income_ratio"]
        cir    = "NULL" if pd.isna(row["credit_income_ratio"]) else row["credit_income_ratio"]
        ann    = "NULL" if pd.isna(row["annuity_amount"]) else row["annuity_amount"]
        rows.append(f"({row['customer_id']}, 20230101, {row['target']}, {row['credit_amount']}, {ann}, {row['income_total']}, {goods}, {dti}, {cir}, {row['ext_source_mean']}, $${row['contract_type']}$$, $${row['income_type']}$$, $${row['education_type']}$$, {row['region_rating']}, {row['age_years']}, {row['employment_years']}, '{row['ingestion_timestamp']}')")
    cursor.execute(f"INSERT INTO fact_loans (customer_id, date_key, target, credit_amount, annuity_amount, income_total, goods_price, debt_to_income_ratio, credit_income_ratio, ext_source_mean, contract_type, income_type, education_type, region_rating, age_years, employment_years, ingestion_timestamp) VALUES {','.join(rows)}")
    if i % 10000 == 0:
        print(f"  fact_loans: {i:,} / {len(fact):,}")
print("fact_loans loaded")

# ── Step 7: Verify row counts ───────────────────────────────
print("\n── Row count verification ──")
for table in ["dim_customers","dim_applications","dim_date","fact_loans"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count:,} rows")

cursor.close()
conn.close()
print("\nAll done — star schema loaded successfully!")