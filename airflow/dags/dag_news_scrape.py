from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator

import sys
sys.path.append('/opt/airflow/dags')
from custom_classes.news import News

default_args = {
    'owner': 'matea',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id='dag_diplomski_v1',
    description='first dag that we write',
    default_args=default_args,
    start_date=datetime(2024,8,21,4),
    schedule_interval='@daily'
) as dag:
    run_fetch_news = PythonOperator(
    dag = dag,
    task_id = 'run_fetch_news',
    python_callable = News().fetch_news
    )

    run_fetch_news

