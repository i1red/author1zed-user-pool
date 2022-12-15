from pydantic import BaseSettings


class PostgresSettings(BaseSettings):
    user: str
    password: str
    host: str
    database: str

    class Config:
        env_prefix = "postgres_"


class RedisSettings(BaseSettings):
    host: str
    port: int
    password: str

    class Config:
        env_prefix = "redis_"
