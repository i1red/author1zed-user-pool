from functools import lru_cache
from typing import TypeVar, Type, Callable

from pydantic import BaseSettings


TSettings = TypeVar("TSettings", bound="BaseSettings")


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


class AuthSettings(BaseSettings):
    auth_expiration_time: int
    auth_code_ttl: int


class JwtSettings(BaseSettings):
    access_token_ttl: int
    refresh_token_ttl: int
    access_token_secret_key: str
    refresh_token_secret_key: str
    algorithm: str

    class Config:
        env_prefix = "jwt_"


def settings_provider(settings_type: Type[TSettings]) -> Callable[[], TSettings]:
    settings = settings_type()

    @lru_cache
    def provide_settings() -> TSettings:
        return settings

    return provide_settings
