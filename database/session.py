from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from database.models import BaseModel
from settings import PostgresSettings


def _get_connection_string() -> str:
    postgres_settings = PostgresSettings()
    return f"postgresql+psycopg2://{postgres_settings.user}:{postgres_settings.password}"\
           f"@{postgres_settings.host}/{postgres_settings.database}"


ENGINE: Final[Engine] = create_engine(_get_connection_string())
BaseModel.metadata.create_all(ENGINE)

Session = sessionmaker(ENGINE)
