import logging
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

import appsettings as settings
import logger

from national_gas.national_gas import NationalGas
from entsog.entsog import ENTSOG
from weather.extract_weather import OpenMeteoWeather

APP_NAME = "gas_data"

logger.setup_log(
    app=APP_NAME,
    filename=os.path.join(settings.LOG_DIR, APP_NAME + ".log"),
    use_stream=True,
)

if __name__ == "__main__":
    try:
        NationalGas().scrape()
        ENTSOG().scrape()
        OpenMeteoWeather().scrape()
    except Exception as e:
        logging.error("Error: %s", traceback.format_exc())
        raise
