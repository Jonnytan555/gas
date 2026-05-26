import logging
import requests

_BASE_URL = "https://api.open-meteo.com/v1/forecast"
_HOURLY   = "temperature_2m,wind_speed_10m,precipitation,surface_pressure"


class OpenMeteoRequestHandler:
    """Fetches hourly forecast from Open-Meteo for each location."""

    def __init__(self, locations: dict, forecast_days: int = 7) -> None:
        self.locations     = locations
        self.forecast_days = forecast_days

    def handle(self) -> list[dict]:
        results = []
        for city, (lat, lon) in self.locations.items():
            resp = requests.get(_BASE_URL, params={
                "latitude":        lat,
                "longitude":       lon,
                "hourly":          _HOURLY,
                "wind_speed_unit": "ms",
                "timezone":        "UTC",
                "forecast_days":   self.forecast_days,
            }, timeout=30)
            resp.raise_for_status()
            results.append({"city": city, "data": resp.json()})
            logging.info("[OpenMeteo] Fetched %s", city)
        return results
