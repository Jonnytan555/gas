import logging
import os
import pandas as pd

from scraper.persistence.persistence_handler import PersistenceHandler
from scraper.request.request_handler import RequestHandler
from scraper.response.response_handler import ResponseHandler
from typing import Callable


class Scraper:

    def __init__(self,
                 request_handler: RequestHandler,
                 response_handler: ResponseHandler,
                 persistence_handler: PersistenceHandler,
                 publish_handler: Callable[[list[dict]], None] | None = None,
                 parquet_path: str | None = None) -> None:
        self.request_handler = request_handler
        self.response_handler = response_handler
        self.persistence_handler = persistence_handler
        self.publish_handler = publish_handler
        self.parquet_path = parquet_path

    def scrape(self,
               dropNa: bool = True,
               dtype=None,
               created_date_column: str = 'CreatedDate'):

        response = self.request_handler.handle()
        result = self.response_handler.handle(response)
        self._save_parquet(result)
        persisted = self.persistence_handler.handle(result, dropNa, dtype, created_date_column)
        self._publish(persisted)
        return persisted

    def _save_parquet(self, df: pd.DataFrame) -> None:
        if not self.parquet_path:
            return
        os.makedirs(os.path.dirname(self.parquet_path) or ".", exist_ok=True)
        df.to_parquet(self.parquet_path, index=False)
        logging.info("[Scraper] Saved %d rows to parquet → %s", len(df), self.parquet_path)

    def _publish(self, persisted: pd.DataFrame | list) -> None:
        if not self.publish_handler or persisted is None:
            return
        rows = persisted if isinstance(persisted, list) else persisted.to_dict(orient="records")
        if not rows:
            return
        try:
            self.publish_handler(rows)
        except Exception as e:
            logging.warning("[Scraper] Publish failed, scrape result unaffected. %s", repr(e))
