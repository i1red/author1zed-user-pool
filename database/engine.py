from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from database.models import META_DATA
from settings import PostgresSettings


def _get_connection_string() -> str:
    postgres_settings = PostgresSettings()
    return f"postgresql+psycopg2://{postgres_settings.user}:{postgres_settings.password}"\
           f"@{postgres_settings.host}/{postgres_settings.database}"


ENGINE: Final[Engine] = create_engine(_get_connection_string())
META_DATA.create_all(ENGINE)
