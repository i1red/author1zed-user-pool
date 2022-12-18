from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from database.abstract.repositories.client_repository import ClientRepository
from database.abstract.repositories.user_repository import UserRepository
from database.sqlalchemy.models import BaseModel
from database.sqlalchemy.repositories.sqlalchemy_client_repository import SqlAlchemyClientRepository
from database.sqlalchemy.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from settings import PostgresSettings


def _get_connection_string() -> str:
    postgres_settings = PostgresSettings()
    return (
        f"postgresql+psycopg2://{postgres_settings.user}:{postgres_settings.password}"
        f"@{postgres_settings.host}/{postgres_settings.database}"
    )


ENGINE: Final[Engine] = create_engine(_get_connection_string())
BaseModel.metadata.create_all(ENGINE)

Session = sessionmaker(ENGINE)


def create_user_repository() -> UserRepository:
    return SqlAlchemyUserRepository(Session())


def create_client_repository() -> ClientRepository:
    return SqlAlchemyClientRepository(Session())
