
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import boto3
import psycopg2
import os

default_args = {
    "owner": "prasad",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

dag = DAG(
    "banking_daily_pipeline",
    default_args=default_args,
    description="Daily banking ETL pipeline — Glue to Redshift to dbt",
    schedule="0 6 * * *",
    catchup=False,
    tags=["banking", "etl", "daily"],
)

def trigger_glue_job():
    client = boto3.client("glue", region_name="us-east-1")
    response = client.start_job_run(JobName="banking-etl-job")
    run_id = response["JobRunId"]
    print(f"Glue job started — Run ID: {run_id}")
    return run_id

def wait_for_glue(**context):
    import time
    run_id = context["ti"].xcom_pull(task_ids="trigger_glue_job")
    client = boto3.client("glue", region_name="us-east-1")
    while True:
        response = client.get_job_run(JobName="banking-etl-job", RunId=run_id)
        status = response["JobRun"]["JobRunState"]
        print(f"Glue job status: {status}")
        if status == "SUCCEEDED":
            print("Glue job completed successfully")
            break
        elif status in ["FAILED", "ERROR", "TIMEOUT"]:
            raise Exception(f"Glue job failed with status: {status}")
        time.sleep(30)

def data_quality_check():
    conn = psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=os.getenv("REDSHIFT_PORT"),
        dbname=os.getenv("REDSHIFT_DB"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD"),
        sslmode="require",
    )
    cursor = conn.cursor()
    checks = {
        "fact_loans row count": "SELECT COUNT(*) FROM fact_loans",
        "null customer_ids": "SELECT COUNT(*) FROM fact_loans WHERE customer_id IS NULL",
        "null targets": "SELECT COUNT(*) FROM fact_loans WHERE target IS NULL",
        "negative credit amounts": "SELECT COUNT(*) FROM fact_loans WHERE credit_amount <= 0",
    }
    print("Running data quality checks...")
    for check_name, query in checks.items():
        cursor.execute(query)
        result = cursor.fetchone()[0]
        print(f"  {check_name}: {result:,}")
        if "null" in check_name.lower() and result > 0:
            raise Exception(f"Data quality check failed: {check_name} = {result}")
        if "negative" in check_name.lower() and result > 0:
            raise Exception(f"Data quality check failed: {check_name} = {result}")
    print("All data quality checks passed")
    cursor.close()
    conn.close()

def notify_success():
    print("=" * 55)
    print("Pipeline completed successfully!")
    print(f"Timestamp: {datetime.utcnow()}")
    print("Tables updated: fact_loans, dim_customers, dim_applications")
    print("=" * 55)

t1_trigger_glue = PythonOperator(
    task_id="trigger_glue_job",
    python_callable=trigger_glue_job,
    dag=dag,
)

t2_wait_glue = PythonOperator(
    task_id="wait_for_glue",
    python_callable=wait_for_glue,
    dag=dag,
)

t3_run_dbt = BashOperator(
    task_id="run_dbt_build",
    bash_command="cd ~/Downloads/Retail-Banking-Customer-Analytics-Platform/dbt && dbt build",
    dag=dag,
)

t4_data_quality = PythonOperator(
    task_id="data_quality_check",
    python_callable=data_quality_check,
    dag=dag,
)

t5_notify = PythonOperator(
    task_id="notify_success",
    python_callable=notify_success,
    dag=dag,
)

t1_trigger_glue >> t2_wait_glue >> t3_run_dbt >> t4_data_quality >> t5_notify
