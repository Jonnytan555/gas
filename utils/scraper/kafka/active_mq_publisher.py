import json
import logging
from typing import Any


class ActiveMqPublisher:
    """Publishes rows to an ActiveMQ destination via STOMP."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        destination: str,
    ) -> None:
        self.host        = host
        self.port        = port
        self.username    = username
        self.password    = password
        self.destination = destination
        self._conn       = None

    def _get_conn(self):
        import stomp
        if self._conn is None or not self._conn.is_connected():
            self._conn = stomp.StompConnection12([(self.host, self.port)])
            self._conn.connect(self.username, self.password, wait=True)
            logging.info("[ActiveMqPublisher] Connected to %s:%s", self.host, self.port)
        return self._conn

    def __call__(self, rows: list[dict[str, Any]]) -> None:
        conn = self._get_conn()
        conn.send(self.destination, json.dumps(rows, default=str))
        logging.info("[ActiveMqPublisher] Published %d rows to %s", len(rows), self.destination)

    def close(self) -> None:
        if self._conn and self._conn.is_connected():
            self._conn.disconnect()
            self._conn = None
