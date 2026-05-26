import sqlalchemy as sa
import appsettings as settings

engine = sa.create_engine(
    f"mssql+pyodbc://{settings.DB_HOST}/{settings.DB_NAME}"
    f"?driver={settings.DB_DRIVER.replace(' ', '+')}"
)
