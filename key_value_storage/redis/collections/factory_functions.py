import datetime

from redis.client import Redis

from entities.auth_code_data import AuthCodeData
from entities.auth_info import AuthInfo
from key_value_storage.redis.collections.redis_string_set import RedisStringSet
from key_value_storage.redis.collections.redis_string_to_dataclass_map import (
    RedisStringToDataclassMap,
)


def create_redis_auth_code_collection(
    redis_client: Redis, default_ttl: datetime.timedelta
) -> RedisStringToDataclassMap[AuthCodeData]:
    return RedisStringToDataclassMap(
        redis_client,
        object_type=AuthCodeData,
        collection_prefix="auth_code",
        ttl=default_ttl,
    )


def create_redis_auth_info_collection(
    redis_client: Redis, default_ttl: datetime.timedelta
) -> RedisStringToDataclassMap[AuthInfo]:
    return RedisStringToDataclassMap(
        redis_client,
        object_type=AuthInfo,
        collection_prefix="auth_info",
        ttl=default_ttl,
    )


def create_redis_refresh_token_collection(redis_client: Redis, default_ttl: datetime.timedelta) -> RedisStringSet:
    return RedisStringSet(redis_client, collection_prefix="refresh_token", ttl=default_ttl)
