# Gas Data Scraper

Collects UK natural gas market data from three public sources, writes to SQL Server, and publishes event triggers to ActiveMQ so downstream consumers (e.g. the gas demand model) can react in real time.

---

## Data Sources

| Source | Protocol | Data | Table |
|--------|----------|------|-------|
| National Gas REST API | POST | Demand, supply, linepack (mcm/d) | `NationalGasData` |
| ENTSOG Transparency Platform | GET | Capacity restrictions & outages (UMMs) | `ENTSOGUrgentMarketMessages` |
| ECMWF GRIB2 files | Local file | Temperature, wind, precipitation at 8 UK cities | `ECMWFForecast` |

---

## Architecture

```
main.py
├── NationalGas.scrape()
│     ├── HttpPostRequestHandler  →  POST api.nationalgas.com/publications/gasday
│     ├── NgtResponseHandler      →  DataFrame (applicable_at, data_item, value)
│     ├── DbUpsertHandler         →  NationalGasData
│     └── ActiveMqPublisher       →  /queue/gas.national
│
└── ENTSOG.scrape()
      ├── HttpGetRequestHandler   →  GET transparency.entsog.eu/urgentMarketMessages
      ├── EnsogResponseHandler    →  DataFrame (active UMMs, unavailableCapacity > 0)
      ├── DbUpsertHandler         →  ENTSOGUrgentMarketMessages
      └── ActiveMqPublisher       →  /queue/gas.entsog

extract_weather.py  (triggered separately when GRIB2 files arrive)
├── cfgrib / xarray  →  GRIB2 file (2t, tp, msl, 10u, 10v)
├── Point extraction at 8 UK cities (nearest grid point)
├── Unit conversion  (K→°C, m→mm, Pa→hPa, u/v→wind speed)
├── DbUpsertHandler  →  ECMWFForecast
└── ActiveMqPublisher  →  /queue/gas.weather
```

---

## Scraper Pattern

Every scraper is assembled from four injectable components wired together by `Scraper`:

```python
Scraper(
    request_handler=HttpPostRequestHandler(url=..., json=..., headers=...),
    response_handler=NgtResponseHandler(data_item_map=...),
    persistence_handler=DbUpsertHandler(engine, table_name, schema, key_cols),
    publish_handler=ActiveMqPublisher(destination=..., host=..., port=...),
).scrape(dropNa=False)
```

`Scraper` calls each handler in order: **request → response → persist → publish**.  
Any step can be swapped without touching the others.

### Component contracts

| Component | Abstract base | Implement | Returns |
|-----------|--------------|-----------|---------|
| `RequestHandler` | `scraper.request.request_handler` | `handle() -> Response` | HTTP response |
| `ResponseHandler` | `scraper.response.response_handler` | `handle(response) -> pd.DataFrame` | Parsed data |
| `PersistenceHandler` | `scraper.persistence.persistence_handler` | `handle(df, ...) -> list[dict]` | Inserted rows |
| `PublishHandler` | `Callable[[list[dict]], None]` | callable | — |

All abstract bases live in `C:\Python\common_libraries\common-scraper\src\scraper\`.  
Project-specific response handlers live in `utils/scraper/response/`.

---

## Adding a New Data Source

**1. Create a response handler** in `utils/scraper/response/my_source_handler.py`:

```python
import pandas as pd
from scraper.response.response_handler import ResponseHandler

class MySourceResponseHandler(ResponseHandler):
    def handle(self, response) -> pd.DataFrame:
        data = response.json()
        # parse into flat rows
        return pd.DataFrame(rows)
```

**2. Create a scraper class** (e.g. `my_source.py`):

```python
from scraper.scraper import Scraper
from scraper.request.get_request import HttpGetRequestHandler
from scraper.persistence.db_upsert_handler import DbUpsertHandler
from scraper.kafka.active_mq_publisher import ActiveMqPublisher
from utils.scraper.response.my_source_handler import MySourceResponseHandler
import appsettings as settings
import sqlalchemy as sa

class MySource:
    def __init__(self):
        self.engine    = sa.create_engine(...)
        self.publisher = ActiveMqPublisher(
            destination="/queue/my.source",
            host=settings.MQ_HOST, port=settings.MQ_PORT,
            username=settings.MQ_USER, password=settings.MQ_PASS,
        )

    def scrape(self):
        Scraper(
            request_handler=HttpGetRequestHandler(url="https://...", params={...}),
            response_handler=MySourceResponseHandler(),
            persistence_handler=DbUpsertHandler(
                engine=self.engine,
                table_name="MySourceData",
                schema="dbo",
                key_cols=["id"],
            ),
            publish_handler=self.publisher,
        ).scrape(dropNa=False)
```

**3. Add to `main.py`**:

```python
from my_source import MySource
MySource().scrape()
```

**4. Create the target SQL Server table** (DbUpsertHandler does not auto-create):

```sql
CREATE TABLE [dbo].[MySourceData] (
    [id]         NVARCHAR(200) NOT NULL,
    ...
    CONSTRAINT PK_MySourceData PRIMARY KEY ([id])
);
```

---

## Configuration

Edit `appsettings.py`:

```python
DB_HOST   = "localhost"
DB_NAME   = "GAS_MODEL"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

NGT_BASE_URL   = "https://api.nationalgas.com/operationaldata/v1"
NGT_DATA_ITEMS = {
    "actual_demand":   "PUBOB637",
    "demand_forecast": "PUBOB28",
    "total_supply":    "PUBOB692",
    "linepack":        "PUBOB693",
}

ENTSOG_BASE_URL     = "https://transparency.entsog.eu/api/v1"
ENTSOG_FORWARD_DAYS = 30   # days ahead to fetch UMMs

MQ_HOST = "localhost"
MQ_PORT = 61613
MQ_USER = "admin"
MQ_PASS = "admin"

GRIB_DIR = r"C:\Temp\WeatherDownloader"   # where ECMWF GRIB2 files land

LOCATIONS = {
    "london":     (51.5,  -0.1),
    "birmingham": (52.5,  -1.9),
    # ... 8 UK cities
}
```

---

## Prerequisites

### SQL Server

Create the `GAS_MODEL` database and run the following DDL:

```sql
USE GAS_MODEL;

CREATE TABLE [dbo].[NationalGasData] (
    [applicable_at] NVARCHAR(50)  NOT NULL,
    [data_item]     NVARCHAR(100) NOT NULL,
    [value]         FLOAT         NULL,
    [unit]          NVARCHAR(20)  NULL,
    [created_at]    NVARCHAR(50)  NULL,
    CONSTRAINT PK_NationalGasData PRIMARY KEY ([applicable_at], [data_item])
);

CREATE TABLE [dbo].[ECMWFForecast] (
    [run_date]   NVARCHAR(20) NOT NULL,
    [location]   NVARCHAR(50) NOT NULL,
    [step_hours] INT          NOT NULL,
    [t2m_c]      FLOAT NULL, [wind_ms] FLOAT NULL,
    [tp_mm]      FLOAT NULL, [msl_hpa] FLOAT NULL,
    [created_at] NVARCHAR(50) NULL,
    CONSTRAINT PK_ECMWFForecast PRIMARY KEY ([run_date], [location], [step_hours])
);

CREATE TABLE [dbo].[ENTSOGUrgentMarketMessages] (
    [id]                      NVARCHAR(200) NOT NULL,
    [messageId]               NVARCHAR(200) NULL,
    [messageType]             NVARCHAR(100) NULL,
    [eventStatus]             NVARCHAR(50)  NULL,
    [eventType]               NVARCHAR(100) NULL,
    [eventStart]              NVARCHAR(50)  NULL,
    [eventStop]               NVARCHAR(50)  NULL,
    [unavailableCapacity]     FLOAT         NULL,
    [availableCapacity]       FLOAT         NULL,
    [technicalCapacity]       FLOAT         NULL,
    [affectedAssetName]       NVARCHAR(500) NULL,
    [affectedAssetEic]        NVARCHAR(100) NULL,
    [balancingZoneName]       NVARCHAR(200) NULL,
    [direction]               NVARCHAR(50)  NULL,
    [unitMeasure]             NVARCHAR(50)  NULL,
    [remarks]                 NVARCHAR(MAX) NULL,
    [lastUpdateDateTime]      NVARCHAR(50)  NULL,
    [isLatestVersion]         NVARCHAR(10)  NULL,
    [isArchived]              NVARCHAR(10)  NULL,
    [CreatedDate]             NVARCHAR(50)  NULL,
    CONSTRAINT PK_ENTSOGUmm PRIMARY KEY ([id])
);
```

### ActiveMQ

```bash
docker run -d --name activemq --restart unless-stopped \
  -p 61613:61613 -p 8161:8161 \
  apache/activemq-classic:latest
```

Web console: `http://localhost:8161` (admin / admin)

---

## Running

```bash
# Daily scrape — NGT demand + ENTSOG UMMs
python main.py

# Weather extraction — run when a new GRIB2 file arrives
python extract_weather.py                        # latest file in GRIB_DIR
python extract_weather.py C:/path/to/file.grib2  # specific file
```

---

## ActiveMQ Queues

| Queue | Published by | Consumed by |
|-------|-------------|-------------|
| `/queue/gas.national` | `national_gas.py` | Gas model listener |
| `/queue/gas.entsog` | `entsog.py` | Gas model listener |
| `/queue/gas.weather` | `extract_weather.py` | Gas model listener |

---

## Database Schema Summary

| Table | Key columns | Source |
|-------|-------------|--------|
| `NationalGasData` | `applicable_at`, `data_item` | National Gas REST API |
| `ECMWFForecast` | `run_date`, `location`, `step_hours` | ECMWF GRIB2 / Open-Meteo |
| `ENTSOGUrgentMarketMessages` | `id` | ENTSOG Transparency Platform |
