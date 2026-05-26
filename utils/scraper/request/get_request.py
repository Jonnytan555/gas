import logging
import requests
from scraper.request.request_handler import RequestHandler


class HttpGetRequestHandler(RequestHandler):

    def handle(self):
        try:
            logging.info(
                "[GET] Requesting from url %s with params %s...",
                self.url,
                self._redact_params(self.params),
            )
            response = requests.get(
                url=self.url,
                params=self.params,
                headers=self.headers,
                auth=self.auth,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logging.error(
                "An error occurred while getting data from %s. Exception: %s",
                self.url,
                repr(e),
            )
            raise e

    def _redact_params(self, params):
        if params is None:
            return
        sensitive_params = ["password", "api_key", "apikey", "secret", "token"]
        return {
            k: ("****" if any(s in k.lower() for s in sensitive_params) else v)
            for k, v in params.items()
        }
