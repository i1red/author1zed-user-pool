import dataclasses
import datetime
from typing import Optional, Final

from redis_data.client import get_client


AUTH_INFO_KEY_PREFIX: Final[str] = "auth_info:"


@dataclasses.dataclass
class AuthInfo:
    client_id: str
    redirect_uri: str
    state: str


def save_auth_info(auth_info_key: str, auth_info: AuthInfo) -> None:
    redis_client = get_client()
    auth_info_key = AUTH_INFO_KEY_PREFIX + auth_info_key

    pipeline = redis_client.pipeline()

    pipeline.multi()

    for key, value in dataclasses.asdict(auth_info).items():
        pipeline.hset(auth_info_key, key, value)

    pipeline.expire(auth_info_key, time=datetime.timedelta(minutes=10))

    pipeline.execute()


def get_auth_info(auth_info_key: str) -> Optional[AuthInfo]:
    redis_client = get_client()
    auth_info_key = AUTH_INFO_KEY_PREFIX + auth_info_key

    auth_info_dict = redis_client.hgetall(auth_info_key)
    if not auth_info_dict:
        return None

    return AuthInfo(**auth_info_dict)


def remove_auth_info(auth_info_key: str) -> None:
    redis_client = get_client()
    auth_info_key = AUTH_INFO_KEY_PREFIX + auth_info_key
    redis_client.delete(auth_info_key)
