from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'matea',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

def get_sklearn():
    import sklearn
    print(sklearn.__version__)

def get_matplotlib():
    import matplotlib
    print(matplotlib.__version__)

with DAG(
    dag_id='dag_with_py_dependencies_v1',
    description='first dag that we write',
    default_args=default_args,
    start_date=datetime(2024,8,21,4),
    schedule_interval='@daily'
) as dag:
    get_sklearn = PythonOperator(
        task_id='get_sk',
        python_callable=get_sklearn
    )
    get_matplotlib = PythonOperator(
        task_id='get_ml',
        python_callable=get_matplotlib
    )

    get_sklearn
    get_matplotlib
