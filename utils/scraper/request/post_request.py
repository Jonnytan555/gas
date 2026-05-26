import logging
import requests
from scraper.request.request_handler import RequestHandler


class HttpPostRequestHandler(RequestHandler):
    def __init__(
        self,
        url: str,
        json=None,
        data=None,
        params=None,
        headers=None,
        auth=None,
        timeout: int = 120,
    ) -> None:
        super().__init__(url, params, headers, auth, timeout=timeout)
        self.json = json
        self.data = data

    def handle(self):
        try:
            logging.info(
                "[POST] Requesting from url %s with body %s...",
                self.url,
                self.json or self.data,
            )
            response = requests.post(
                url=self.url,
                json=self.json,
                data=self.data,
                params=self.params,
                headers=self.headers,
                auth=self.auth,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logging.error(
                "An error occurred while posting to %s. Exception: %s",
                self.url,
                repr(e),
            )
            raise e
