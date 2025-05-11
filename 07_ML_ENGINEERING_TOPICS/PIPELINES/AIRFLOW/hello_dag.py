from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    dag_id='hello_composer_dag',
    schedule_interval='@daily',
    catchup=False,
    default_args=default_args,
    tags=['tutorial'],
) as dag:
    
    hello_task = BashOperator(
        task_id='print_hello',
        bash_command='echo "Hello from Cloud Composer!"'
    )