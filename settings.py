from pydantic import BaseSettings


class PostgresSettings(BaseSettings):
    user: str
    password: str
    host: str
    database: str

    class Config:
        env_prefix = "postgres_"
