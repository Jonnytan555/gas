import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import sqlalchemy as sa
from retry import retry

sys.path.insert(0, str(Path(__file__).parent))             # for appsettings
sys.path.insert(0, str(Path(__file__).parent.parent))      # for gas/ root
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))  # for scraper utils

import appsettings as settings
from scraper.scraper import Scraper
from scraper.request.post_request import HttpPostRequestHandler
from scraper.persistence.db_upsert_handler import DbUpsertHandler
from scraper.kafka.active_mq_publisher import ActiveMqPublisher
from scraper.response.ngt_response_handler import NgtResponseHandler


class NationalGas:

    def __init__(self):
        self.engine    = sa.create_engine(
            f"mssql+pyodbc://{settings.DB_HOST}/{settings.DB_NAME}"
            f"?driver={settings.DB_DRIVER.replace(' ', '+')}"
        )
        self.publisher = ActiveMqPublisher(
            destination=settings.MQ_QUEUE_NATIONAL,
            host=settings.MQ_HOST, port=settings.MQ_PORT,
            username=settings.MQ_USER, password=settings.MQ_PASS,
        )

    @retry(tries=5, delay=2, backoff=2)
    def scrape(self, gas_date: Optional[date] = None):
        gas_date = gas_date or date.today() - timedelta(days=1)
        date_str = gas_date.isoformat()

        Scraper(
            request_handler=HttpPostRequestHandler(
                url=f"{settings.NGT_BASE_URL}/publications/gasday",
                json={
                    "fromDate":       date_str,
                    "toDate":         date_str,
                    "publicationIds": list(settings.NGT_DATA_ITEMS.values()),
                    "latestValue":    "Y",
                },
                headers={"Content-Type": "application/json"},
            ),
            response_handler=NgtResponseHandler(
                data_item_map=settings.NGT_DATA_ITEMS
            ),
            persistence_handler=DbUpsertHandler(
                engine=self.engine,
                table_name="NationalGasData",
                schema="dbo",
                key_cols=["applicable_at", "data_item"],
            ),
            publish_handler=self.publisher,
        ).scrape(dropNa=False)
