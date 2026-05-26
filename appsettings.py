import os

DB_HOST   = os.environ.get("DB_HOST",   "localhost")
DB_NAME   = os.environ.get("DB_NAME",   "GAS_MODEL")
DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# National Gas Transmission — REST API (public, no auth)
# https://api.nationalgas.com/operationaldata/v1/publications/gasday  (POST)
NGT_BASE_URL  = "https://api.nationalgas.com/operationaldata/v1"
NGT_DATA_ITEMS = {
    "actual_demand":   "PUBOB637",  # Demand Actual, NTS, D+1
    "demand_forecast": "PUBOB28",   # Demand Forecast, NTS, hourly update
    "total_supply":    "PUBOB692",  # NTS System Input, Actual
    "linepack":        "PUBOB693",  # Opening linepack, actual
}

# ENTSOG Transparency Platform (public, no auth)
# UMMs: outage and capacity restriction notices relevant to UK gas supply
ENTSOG_BASE_URL      = "https://transparency.entsog.eu/api/v1"
ENTSOG_FORWARD_DAYS  = 30   # how far ahead to fetch UMMs

# ActiveMQ — event triggers for the gas model listener
MQ_HOST = os.environ.get("MQ_HOST", "localhost")
MQ_PORT = int(os.environ.get("MQ_PORT", "61613"))
MQ_USER = os.environ.get("MQ_USER", "admin")
MQ_PASS = os.environ.get("MQ_PASS", "admin")

MQ_QUEUE_NATIONAL = "/queue/gas.national"
MQ_QUEUE_ENTSOG   = "/queue/gas.entsog"
MQ_QUEUE_WEATHER  = "/queue/gas.weather"
MQ_QUEUE_FORECAST = "/queue/gas.forecast"

# Paths
LOG_DIR             = os.environ.get("LOG_DIR",             r"C:\Python\Scrapes\gas\logs")
GRIB_DIR            = os.environ.get("GRIB_DIR",            r"C:\Temp\WeatherDownloader")
WEATHER_PLOTTER_DIR = os.environ.get("WEATHER_PLOTTER_DIR", r"C:\Python\DataEngineering\Weather\WeatherPlotter")

# UK demand centres for weather point extraction (latitude, longitude)
LOCATIONS = {
    "london":     (51.5,  -0.1),
    "birmingham": (52.5,  -1.9),
    "manchester": (53.5,  -2.2),
    "leeds":      (53.8,  -1.5),
    "glasgow":    (55.9,  -4.3),
    "edinburgh":  (55.9,  -3.2),
    "cardiff":    (51.5,  -3.2),
    "belfast":    (54.6,  -5.9),
}
