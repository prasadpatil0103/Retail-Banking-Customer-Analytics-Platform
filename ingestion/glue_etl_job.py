import sys
import logging
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import datetime

# ── Logging setup ──────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Job parameters ─────────────────────────────────────────
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ── Config ─────────────────────────────────────────────────
S3_INPUT  = "s3://retail-banking-analytics-prasad/raw/home-credit/"
S3_OUTPUT = "s3://retail-banking-analytics-prasad/cleaned/"

# ── Helper: log row counts ──────────────────────────────────
def log_counts(df, name):
    count = df.count()
    logger.info(f"[{name}] Row count: {count:,}")
    return count

# ── Helper: null % check ────────────────────────────────────
def check_nulls(df, name, threshold=0.5):
    total = df.count()
    for col_name in df.columns:
        null_pct = df.filter(F.col(col_name).isNull()).count() / total
        if null_pct > threshold:
            logger.warning(f"[{name}] Column '{col_name}' has {null_pct:.1%} nulls")

# ════════════════════════════════════════════════════════════
# 1. APPLICATION TRAIN
# ════════════════════════════════════════════════════════════
logger.info("Processing application_train.csv ...")

app_train = spark.read.csv(
    S3_INPUT + "application_train.csv",
    header=True, inferSchema=True
)

# Rename columns to snake_case
app_train = app_train \
    .withColumnRenamed("SK_ID_CURR", "customer_id") \
    .withColumnRenamed("TARGET", "target") \
    .withColumnRenamed("NAME_CONTRACT_TYPE", "contract_type") \
    .withColumnRenamed("AMT_CREDIT", "credit_amount") \
    .withColumnRenamed("AMT_ANNUITY", "annuity_amount") \
    .withColumnRenamed("AMT_INCOME_TOTAL", "income_total") \
    .withColumnRenamed("AMT_GOODS_PRICE", "goods_price") \
    .withColumnRenamed("NAME_INCOME_TYPE", "income_type") \
    .withColumnRenamed("NAME_EDUCATION_TYPE", "education_type") \
    .withColumnRenamed("NAME_FAMILY_STATUS", "family_status") \
    .withColumnRenamed("DAYS_BIRTH", "days_birth") \
    .withColumnRenamed("DAYS_EMPLOYED", "days_employed") \
    .withColumnRenamed("CNT_FAM_MEMBERS", "family_members") \
    .withColumnRenamed("REGION_RATING_CLIENT", "region_rating") \
    .withColumnRenamed("EXT_SOURCE_1", "ext_source_1") \
    .withColumnRenamed("EXT_SOURCE_2", "ext_source_2") \
    .withColumnRenamed("EXT_SOURCE_3", "ext_source_3")

# Derive clean columns
app_train = app_train \
    .withColumn("age_years", (F.abs(F.col("days_birth")) / 365).cast(IntegerType())) \
    .withColumn("employment_years", 
        F.when(F.col("days_employed") > 0, 0)
         .otherwise((F.abs(F.col("days_employed")) / 365).cast(IntegerType()))) \
    .withColumn("debt_to_income_ratio",
        F.round(F.col("annuity_amount") / F.col("income_total"), 4)) \
    .withColumn("credit_income_ratio",
        F.round(F.col("credit_amount") / F.col("income_total"), 4)) \
    .withColumn("ext_source_mean",
        F.round(
            (F.coalesce(F.col("ext_source_1"), F.lit(0)) +
             F.coalesce(F.col("ext_source_2"), F.lit(0)) +
             F.coalesce(F.col("ext_source_3"), F.lit(0))) / 3, 4)) \
    .withColumn("ingestion_timestamp", F.lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

# Filter out invalid rows
app_train = app_train.filter(
    (F.col("customer_id").isNotNull()) &
    (F.col("income_total") > 0) &
    (F.col("credit_amount") > 0)
)

# Data quality check
raw_count = log_counts(app_train, "application_train")
check_nulls(app_train, "application_train")

# Write to S3
app_train.write.mode("overwrite").parquet(S3_OUTPUT + "application_train/")
logger.info("application_train written to S3 cleaned layer")

# ════════════════════════════════════════════════════════════
# 2. BUREAU
# ════════════════════════════════════════════════════════════
logger.info("Processing bureau.csv ...")

bureau = spark.read.csv(
    S3_INPUT + "bureau.csv",
    header=True, inferSchema=True
)

bureau = bureau \
    .withColumnRenamed("SK_ID_CURR", "customer_id") \
    .withColumnRenamed("SK_ID_BUREAU", "bureau_id") \
    .withColumnRenamed("CREDIT_ACTIVE", "credit_active") \
    .withColumnRenamed("CREDIT_TYPE", "credit_type") \
    .withColumnRenamed("AMT_CREDIT_SUM", "credit_sum") \
    .withColumnRenamed("AMT_CREDIT_SUM_DEBT", "credit_debt") \
    .withColumnRenamed("AMT_CREDIT_SUM_OVERDUE", "credit_overdue") \
    .withColumnRenamed("DAYS_CREDIT", "days_credit") \
    .withColumnRenamed("DAYS_ENDDATE_FACT", "days_enddate") \
    .withColumn("ingestion_timestamp", F.lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

bureau = bureau.filter(F.col("customer_id").isNotNull())

log_counts(bureau, "bureau")
bureau.write.mode("overwrite").parquet(S3_OUTPUT + "bureau/")
logger.info("bureau written to S3 cleaned layer")

# ════════════════════════════════════════════════════════════
# 3. PREVIOUS APPLICATION
# ════════════════════════════════════════════════════════════
logger.info("Processing previous_application.csv ...")

prev_app = spark.read.csv(
    S3_INPUT + "previous_application.csv",
    header=True, inferSchema=True
)

prev_app = prev_app \
    .withColumnRenamed("SK_ID_CURR", "customer_id") \
    .withColumnRenamed("SK_ID_PREV", "prev_application_id") \
    .withColumnRenamed("NAME_CONTRACT_TYPE", "contract_type") \
    .withColumnRenamed("AMT_ANNUITY", "annuity_amount") \
    .withColumnRenamed("AMT_APPLICATION", "application_amount") \
    .withColumnRenamed("AMT_CREDIT", "credit_amount") \
    .withColumnRenamed("NAME_CONTRACT_STATUS", "contract_status") \
    .withColumnRenamed("DAYS_DECISION", "days_decision") \
    .withColumn("ingestion_timestamp", F.lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

prev_app = prev_app.filter(F.col("customer_id").isNotNull())

log_counts(prev_app, "previous_application")
prev_app.write.mode("overwrite").parquet(S3_OUTPUT + "previous_application/")
logger.info("previous_application written to S3 cleaned layer")

# ════════════════════════════════════════════════════════════
# 4. INSTALLMENTS PAYMENTS
# ════════════════════════════════════════════════════════════
logger.info("Processing installments_payments.csv ...")

installments = spark.read.csv(
    S3_INPUT + "installments_payments.csv",
    header=True, inferSchema=True
)

installments = installments \
    .withColumnRenamed("SK_ID_CURR", "customer_id") \
    .withColumnRenamed("SK_ID_PREV", "prev_application_id") \
    .withColumnRenamed("NUM_INSTALMENT_VERSION", "instalment_version") \
    .withColumnRenamed("NUM_INSTALMENT_NUMBER", "instalment_number") \
    .withColumnRenamed("DAYS_INSTALMENT", "days_instalment") \
    .withColumnRenamed("DAYS_ENTRY_PAYMENT", "days_payment") \
    .withColumnRenamed("AMT_INSTALMENT", "instalment_amount") \
    .withColumnRenamed("AMT_PAYMENT", "payment_amount") \
    .withColumn("payment_diff",
        F.round(F.col("payment_amount") - F.col("instalment_amount"), 2)) \
    .withColumn("ingestion_timestamp", F.lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

installments = installments.filter(F.col("customer_id").isNotNull())

log_counts(installments, "installments_payments")
installments.write.mode("overwrite").parquet(S3_OUTPUT + "installments_payments/")
logger.info("installments_payments written to S3 cleaned layer")

# ════════════════════════════════════════════════════════════
# 5. CREDIT CARD BALANCE
# ════════════════════════════════════════════════════════════
logger.info("Processing credit_card_balance.csv ...")

cc_balance = spark.read.csv(
    S3_INPUT + "credit_card_balance.csv",
    header=True, inferSchema=True
)

cc_balance = cc_balance \
    .withColumnRenamed("SK_ID_CURR", "customer_id") \
    .withColumnRenamed("SK_ID_PREV", "prev_application_id") \
    .withColumnRenamed("MONTHS_BALANCE", "months_balance") \
    .withColumnRenamed("AMT_BALANCE", "balance_amount") \
    .withColumnRenamed("AMT_CREDIT_LIMIT_ACTUAL", "credit_limit") \
    .withColumnRenamed("AMT_DRAWINGS_CURRENT", "drawings_current") \
    .withColumnRenamed("AMT_PAYMENT_CURRENT", "payment_current") \
    .withColumnRenamed("SK_DPD", "days_past_due") \
    .withColumn("utilization_rate",
        F.round(F.col("balance_amount") / F.col("credit_limit"), 4)) \
    .withColumn("ingestion_timestamp", F.lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

cc_balance = cc_balance.filter(F.col("customer_id").isNotNull())

log_counts(cc_balance, "credit_card_balance")
cc_balance.write.mode("overwrite").parquet(S3_OUTPUT + "credit_card_balance/")
logger.info("credit_card_balance written to S3 cleaned layer")

# ════════════════════════════════════════════════════════════
# 6. POS CASH BALANCE
# ════════════════════════════════════════════════════════════
logger.info("Processing POS_CASH_balance.csv ...")

pos_cash = spark.read.csv(
    S3_INPUT + "POS_CASH_balance.csv",
    header=True, inferSchema=True
)

pos_cash = pos_cash \
    .withColumnRenamed("SK_ID_CURR", "customer_id") \
    .withColumnRenamed("SK_ID_PREV", "prev_application_id") \
    .withColumnRenamed("MONTHS_BALANCE", "months_balance") \
    .withColumnRenamed("CNT_INSTALMENT", "instalment_count") \
    .withColumnRenamed("CNT_INSTALMENT_FUTURE", "instalment_future") \
    .withColumnRenamed("NAME_CONTRACT_STATUS", "contract_status") \
    .withColumnRenamed("SK_DPD", "days_past_due") \
    .withColumn("ingestion_timestamp", F.lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

pos_cash = pos_cash.filter(F.col("customer_id").isNotNull())

log_counts(pos_cash, "POS_CASH_balance")
pos_cash.write.mode("overwrite").parquet(S3_OUTPUT + "POS_CASH_balance/")
logger.info("POS_CASH_balance written to S3 cleaned layer")

# ════════════════════════════════════════════════════════════
# Final summary
# ════════════════════════════════════════════════════════════
logger.info("=" * 55)
logger.info("ETL COMPLETE — all 6 tables cleaned and written to S3")
logger.info(f"Output location: {S3_OUTPUT}")
logger.info("=" * 55)

job.commit()