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


class JwtSettings(BaseSettings):
    access_token_lifetime: int
    refresh_token_lifetime: int
    access_token_secret_key: str
    refresh_token_secret_key: str
    algorithm: str

    class Config:
        env_prefix = "jwt_"
