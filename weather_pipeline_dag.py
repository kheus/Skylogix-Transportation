# weather_pipeline_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
from ingestion import fetch_and_upsert
from transform_load import transform_and_load

default_args = {
    'owner': 'skylogix',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'skylogix_weather_pipeline',
    default_args=default_args,
    description='Real-time weather pipeline for SkyLogix Transportation',
    schedule_interval='*/15 * * * *',  # every 15 minutes
    start_date=datetime(2025, 12, 1),
    catchup=False,
    tags=['weather', 'skylogix'],
) as dag:

    t1 = PythonOperator(task_id='fetch_and_upsert_raw', python_callable=fetch_and_upsert)
    t2 = PythonOperator(task_id='transform_and_load_postgres', python_callable=transform_and_load)

    t1 >> t2
