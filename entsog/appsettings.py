import os

# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST   = os.environ.get("DB_HOST",   "localhost")
DB_NAME   = os.environ.get("DB_NAME",   "GAS_MODEL")
DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# ── ActiveMQ ───────────────────────────────────────────────────────────────────
MQ_HOST         = os.environ.get("MQ_HOST", "localhost")
MQ_PORT         = int(os.environ.get("MQ_PORT", "61613"))
MQ_USER         = os.environ.get("MQ_USER", "admin")
MQ_PASS         = os.environ.get("MQ_PASS", "admin")
MQ_QUEUE_ENTSOG = "/queue/gas.entsog"

# ── Paths ──────────────────────────────────────────────────────────────────────
LOG_DIR = os.environ.get("LOG_DIR", r"C:\Python\Scrapes\gas\logs")

# ── ENTSOG Transparency Platform ───────────────────────────────────────────────
ENTSOG_BASE_URL     = "https://transparency.entsog.eu/api/v1"
ENTSOG_FORWARD_DAYS = 30   # how far ahead to fetch UMMs
