import sys
from datetime import datetime, timedelta
from pathlib import Path

import appsettings as settings
import sqlalchemy as sa
from retry import retry

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from scraper.scraper import Scraper
from scraper.request.get_request import HttpGetRequestHandler
from scraper.persistence.db_merge_handler import DbMergeHandler
from scraper.kafka.active_mq_publisher import ActiveMqPublisher
from scraper.response.entsog_response_handler import EnsogResponseHandler


class ENTSOG:

    def __init__(self):
        self.engine    = sa.create_engine(
            f"mssql+pyodbc://{settings.DB_HOST}/{settings.DB_NAME}"
            f"?driver={settings.DB_DRIVER.replace(' ', '+')}"
        )
        self.publisher = ActiveMqPublisher(
            destination=settings.MQ_QUEUE_ENTSOG,
            host=settings.MQ_HOST, port=settings.MQ_PORT,
            username=settings.MQ_USER, password=settings.MQ_PASS,
        )

    @retry(tries=5, delay=2, backoff=2)
    def scrape(self):
        from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        to_date   = (datetime.now() + timedelta(days=settings.ENTSOG_FORWARD_DAYS)).strftime("%Y-%m-%d")

        Scraper(
            request_handler=HttpGetRequestHandler(
                url=f"{settings.ENTSOG_BASE_URL}/urgentMarketMessages",
                params={
                    "messageType":  "all",
                    "from":         from_date,
                    "to":           to_date,
                    "timeZone":     "CET",
                    "eventStatus":  "All",
                    "limit":        "-1",
                    "indicator":    "UMM Data",
                },
                timeout=60,
            ),
            response_handler=EnsogResponseHandler(),
            persistence_handler=DbMergeHandler(
                engine=self.engine,
                table_name="ENTSOGUrgentMarketMessages",
                schema="dbo",
                key_cols=["id"],
            ),
            publish_handler=self.publisher,
        ).scrape(dropNa=False)
