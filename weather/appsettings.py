import os

# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST   = os.environ.get("DB_HOST",   "localhost")
DB_NAME   = os.environ.get("DB_NAME",   "GAS_MODEL")
DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# ── ActiveMQ ───────────────────────────────────────────────────────────────────
MQ_HOST          = os.environ.get("MQ_HOST", "localhost")
MQ_PORT          = int(os.environ.get("MQ_PORT", "61613"))
MQ_USER          = os.environ.get("MQ_USER", "admin")
MQ_PASS          = os.environ.get("MQ_PASS", "admin")
MQ_QUEUE_WEATHER = "/queue/gas.weather"

# ── Paths ──────────────────────────────────────────────────────────────────────
LOG_DIR             = os.environ.get("LOG_DIR",             r"C:\Python\Scrapes\gas\logs")
GRIB_DIR            = os.environ.get("GRIB_DIR",            r"C:\Temp\WeatherDownloader")
WEATHER_PLOTTER_DIR = os.environ.get("WEATHER_PLOTTER_DIR", r"C:\Python\DataEngineering\Weather\WeatherPlotter")

# ── UK demand centres ──────────────────────────────────────────────────────────
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
