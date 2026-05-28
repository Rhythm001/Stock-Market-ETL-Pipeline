from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.extractor import extract_all
from src.loader import load_to_postgres

default_args = {
    'owner': 'rhythm',
    'retries' : 2,
    'retry_delay' : timedelta(minutes=5),
    'email_on_failure' : True,
}
with DAG (
    dag_id = 'stock_market_etl',
    default_args = default_args, 
    schedule = '0 6 * * 1-5',
    start_date = datetime(2024, 1, 1),
    catchup=False,
) as dag:
    extract = PythonOperator(task_id='extract_raw_data', python_callable=extract_all)
    load = PythonOperator(task_id = 'load_to_postgres', python_callable=load_to_postgres)
    # transform = PythonOperator(task_id='run_transformations', python_callable=run_transformations)
    # quality = PythonOperator(task_id='run_quality_checks', python_callable=run_checks)
    # report = PythonOperator(task_id='run_quality_checks', python_callable=generate_report)
    
    extract >> load #>> transform >> quality >> report