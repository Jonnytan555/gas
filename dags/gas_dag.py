from datetime import datetime, timedelta
import sys
import os

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

GAS_PATH = "/opt/airflow/gas"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


def scrape_national_gas():
    sys.path.insert(0, GAS_PATH)
    sys.path.insert(0, os.path.join(GAS_PATH, "utils"))
    from national_gas.national_gas import NationalGas
    NationalGas().scrape()


def scrape_entsog():
    sys.path.insert(0, GAS_PATH)
    sys.path.insert(0, os.path.join(GAS_PATH, "utils"))
    from entsog.entsog import ENTSOG
    ENTSOG().scrape()


def scrape_weather():
    sys.path.insert(0, GAS_PATH)
    sys.path.insert(0, os.path.join(GAS_PATH, "utils"))
    from weather.extract_weather import OpenMeteoWeather
    OpenMeteoWeather().scrape()


with DAG(
    "gas_pipeline",
    default_args=default_args,
    schedule="@hourly",
    catchup=False,
) as dag:

    national_gas_task = PythonOperator(
        task_id="scrape_national_gas",
        python_callable=scrape_national_gas,
    )

    entsog_task = PythonOperator(
        task_id="scrape_entsog",
        python_callable=scrape_entsog,
    )

    weather_task = PythonOperator(
        task_id="scrape_weather",
        python_callable=scrape_weather,
    )

    [national_gas_task, entsog_task, weather_task]
