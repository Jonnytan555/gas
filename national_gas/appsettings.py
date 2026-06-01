import os

# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST   = os.environ.get("DB_HOST",   "localhost")
DB_NAME   = os.environ.get("DB_NAME",   "GAS_MODEL")
DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# ── ActiveMQ ───────────────────────────────────────────────────────────────────
MQ_HOST           = os.environ.get("MQ_HOST", "localhost")
MQ_PORT           = int(os.environ.get("MQ_PORT", "61613"))
MQ_USER           = os.environ.get("MQ_USER", "admin")
MQ_PASS           = os.environ.get("MQ_PASS", "admin")
MQ_QUEUE_NATIONAL = "/queue/gas.national"

# ── Paths ──────────────────────────────────────────────────────────────────────
LOG_DIR = os.environ.get("LOG_DIR", r"C:\Python\Scrapes\gas\logs")

# ── National Gas Transmission API ─────────────────────────────────────────────
NGT_BASE_URL   = "https://api.nationalgas.com/operationaldata/v1"
NGT_DATA_ITEMS = {
    "actual_demand":   "PUBOB637",   # Demand Actual, NTS, D+1
    "demand_forecast": "PUBOB28",    # Demand Forecast, NTS, hourly update
    "total_supply":    "PUBOB692",   # NTS System Input, Actual
    "linepack":        "PUBOB693",   # Opening linepack, actual
}
