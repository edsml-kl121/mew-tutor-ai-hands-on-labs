from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Instantiate the DAG
with DAG(
    dag_id='simple_two_component_dag',
    default_args=default_args,
    description='A simple DAG with two dependent tasks',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Simulate data fetching
    fetch_data = BashOperator(
        task_id='fetch_data',
        bash_command='echo "Fetching data..." && sleep 5',
    )

    # Task 2: Simulate data processing
    process_data = BashOperator(
        task_id='process_data',
        bash_command='echo "Processing data..." && sleep 5',
    )

    # Set task dependencies
    fetch_data >> process_data