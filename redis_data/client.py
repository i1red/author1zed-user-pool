from functools import lru_cache

from redis import Redis
from settings import RedisSettings


@lru_cache
def get_client() -> Redis:
    redis_settings = RedisSettings()
    return Redis(
        host=redis_settings.host, port=redis_settings.port, password=redis_settings.password, decode_responses=True
    )
