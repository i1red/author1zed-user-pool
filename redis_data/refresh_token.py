import datetime
from typing import Final

from redis_data.client import get_client

REFRESH_TOKEN_PREFIX: Final[str] = "refresh_token:"
EMPTY_VALUE: Final[str] = ""


def save_refresh_token(token: str, ttl: int) -> None:
    redis_client = get_client()
    token_key = REFRESH_TOKEN_PREFIX + token

    redis_client.set(token_key, EMPTY_VALUE)
    redis_client.expire(token_key, datetime.timedelta(seconds=ttl))


def check_if_refresh_token_exists(token: str) -> bool:
    redis_client = get_client()
    token_key = REFRESH_TOKEN_PREFIX + token
    return redis_client.get(token_key) is not None


def remove_refresh_token(token: str) -> None:
    redis_client = get_client()
    token_key = REFRESH_TOKEN_PREFIX + token
    redis_client.delete(token_key)
