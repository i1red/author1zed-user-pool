import datetime

from fastapi import Depends
from redis.client import Redis

from objects.auth_code_data import AuthCodeData
from objects.auth_info import AuthInfo
from key_value_storage.abstract.collections.string_set import StringSet
from key_value_storage.abstract.collections.string_to_dataclass_map import StringToDataclassMap
from key_value_storage.redis.collections.factory_functions import (
    create_redis_auth_code_collection,
    create_redis_auth_info_collection,
    create_redis_refresh_token_collection,
)
from settings import RedisSettings, AuthSettings, JwtSettings, settings_provider


def create_redis_client(
    redis_settings: RedisSettings = Depends(settings_provider(RedisSettings)),
) -> Redis:
    return Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        password=redis_settings.password,
        decode_responses=True,
    )


def create_auth_info_collection(
    redis_client: Redis = Depends(create_redis_client),
    auth_settings: AuthSettings = Depends(settings_provider(AuthSettings)),
) -> StringToDataclassMap[AuthInfo]:
    return create_redis_auth_info_collection(
        redis_client,
        default_ttl=datetime.timedelta(seconds=auth_settings.auth_expiration_time),
    )


def create_auth_code_collection(
    redis_client: Redis = Depends(create_redis_client),
    auth_settings: AuthSettings = Depends(settings_provider(AuthSettings)),
) -> StringToDataclassMap[AuthCodeData]:
    return create_redis_auth_code_collection(
        redis_client,
        default_ttl=datetime.timedelta(seconds=auth_settings.auth_code_ttl),
    )


def create_refresh_token_collection(
    redis_client: Redis = Depends(create_redis_client),
    jwt_settings: JwtSettings = Depends(settings_provider(JwtSettings)),
) -> StringSet:
    return create_redis_refresh_token_collection(
        redis_client,
        default_ttl=datetime.timedelta(seconds=jwt_settings.refresh_token_ttl),
    )
