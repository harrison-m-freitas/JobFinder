from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    "workable_daily", schedule="@hourly", start_date=datetime(2025, 1, 1), catchup=False
) as dag:
    BashOperator(task_id="scrape", bash_command="scrapy crawl workable -a org=<org>")
