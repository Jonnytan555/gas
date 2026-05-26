import os
import sys
import sqlalchemy as sa
from pathlib import Path
from retry import retry

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, r"C:\Python\common_libraries\common-scraper\src")

import logger
logger.setup_log(
    app="extract_weather",
    filename=os.path.join(r"C:\Python\Scrapes\gas\logs", "extract_weather.log"),
    use_stream=True,
)

import appsettings as settings
from scraper.scraper import Scraper
from scraper.persistence.db_upsert_handler import DbUpsertHandler
from scraper.kafka.active_mq_publisher import ActiveMqPublisher
from utils.scraper.request.open_meteo_request import OpenMeteoRequestHandler
from utils.scraper.response.open_meteo_response_handler import OpenMeteoResponseHandler

class OpenMeteoWeather:

    def __init__(self):
        self.engine    = sa.create_engine(
            f"mssql+pyodbc://{settings.DB_HOST}/{settings.DB_NAME}"
            f"?driver={settings.DB_DRIVER.replace(' ', '+')}"
        )
        self.publisher = ActiveMqPublisher(
            destination=settings.MQ_QUEUE_WEATHER,
            host=settings.MQ_HOST, port=settings.MQ_PORT,
            username=settings.MQ_USER, password=settings.MQ_PASS,
        )

    @retry(tries=3, delay=5, backoff=2)
    def scrape(self):
        Scraper(
            request_handler=OpenMeteoRequestHandler(
                locations=settings.LOCATIONS,
            ),
            response_handler=OpenMeteoResponseHandler(),
            persistence_handler=DbUpsertHandler(
                engine=self.engine,
                table_name="WeatherForecast",
                schema="dbo",
                key_cols=["valid_time", "location"],
            ),
            publish_handler=self.publisher,
        ).scrape()


if __name__ == "__main__":
    OpenMeteoWeather().scrape()
