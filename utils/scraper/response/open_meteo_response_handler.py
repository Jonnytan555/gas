import pandas as pd
from datetime import datetime, timezone

from scraper.response.response_handler import ResponseHandler


class OpenMeteoResponseHandler(ResponseHandler):

    def __init__(self) -> None:
        super().__init__()

    def handle(self, responses: list[dict]) -> pd.DataFrame:
        created_at = datetime.now(timezone.utc).isoformat()
        rows = []
        for item in responses:
            city   = item["city"]
            hourly = item["data"]["hourly"]
            for i, valid_time in enumerate(hourly["time"]):
                rows.append({
                    "valid_time": valid_time,
                    "location":   city,
                    "t2m_c":      hourly["temperature_2m"][i],
                    "wind_ms":    hourly["wind_speed_10m"][i],
                    "tp_mm":      hourly["precipitation"][i],
                    "msl_hpa":    hourly["surface_pressure"][i],
                    "created_at": created_at,
                })
        return pd.DataFrame(rows)
