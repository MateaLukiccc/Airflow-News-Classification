from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    'owner': 'matea',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

@dag(dag_id='dag_with_taskflow_v3',
     default_args=default_args,
     start_date=datetime(2024,8,21),
     schedule_interval='@daily')
def hello_world_etl():
    
    @task(multiple_outputs=True)
    def get_name():
        return {'first_name': 'Jerry', 'last_name': 'Fridman'}
    
    @task()
    def get_age():
        return 19
    
    @task()
    def greet(first_name, last_name, age):
        print(first_name,last_name, age)

    name = get_name()
    age =get_age()
    greet(name['first_name'], name['last_name'], age)

greet_dag = hello_world_etl()

