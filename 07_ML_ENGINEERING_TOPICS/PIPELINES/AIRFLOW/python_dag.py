from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define your Python functions
def extract_data(**kwargs):
    sample_data = {"name": "ChatGPT", "lang": "Python"}
    print("Extracted data:", sample_data)
    # Pass data via XCom
    kwargs['ti'].xcom_push(key='my_data', value=sample_data)

def transform_data(**kwargs):
    # Pull data from XCom
    data = kwargs['ti'].xcom_pull(key='my_data', task_ids='extract_data')
    transformed = {k: v.upper() for k, v in data.items()}
    print("Transformed data:", transformed)

# Create the DAG
with DAG(
    dag_id='python_two_task_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    description='DAG with two Python tasks tied together',
) as dag:

    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    # Set dependencies
    extract >> transform