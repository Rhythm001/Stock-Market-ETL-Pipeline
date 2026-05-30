from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow')

import os

from src.pipeline import (run_extraction_load, run_transform_task, run_quality_task)
# from src.transformer import run_transformation
# from src.quality_checks import run_checks
from src.report_generator import generate_report


from src.pipeline import (
    run_extraction_load,
    run_transform_task,
    run_quality_task
)

default_args = {
    'owner': 'rhythm',
    'retries' : 2,
    'retry_delay' : timedelta(minutes=5),
    'email_on_failure' : True,
}
with DAG (
    dag_id = 'stock_market_etl',
    default_args = default_args, 
    schedule = "0 6 * * 1-5",
    start_date = datetime(2024, 1, 1),
    catchup=False,
) as dag:
    extract_load = PythonOperator(
        task_id = "extract_and_load_raw",
        python_callable = run_extraction_load
    )
    
    transform = PythonOperator(
        task_id = "run_transformations",
        python_callable = run_transform_task
    )
    
    quality = PythonOperator(
        task_id = "run_quality_checks",
        python_callable = run_quality_task
    )
    
    report = PythonOperator(
        task_id = "generate_report",
        python_callable  = generate_report
    )
    
    extract_load >> transform >> quality >> report
    
    
