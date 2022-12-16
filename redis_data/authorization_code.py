import dataclasses
import datetime
from typing import Final, Optional

from redis_data.client import get_client


AUTH_CODE_PREFIX: Final[str] = "auth_code:"


@dataclasses.dataclass
class AuthCodeData:
    client_id: str
    user_id: int


def save_auth_code_data(code: str, auth_code_data: AuthCodeData) -> None:
    redis_client = get_client()

    code_key = AUTH_CODE_PREFIX + code

    pipeline = redis_client.pipeline()

    pipeline.multi()

    for key, value in dataclasses.asdict(auth_code_data).items():
        pipeline.hset(code_key, key, value)

    pipeline.expire(code_key, time=datetime.timedelta(minutes=10))

    pipeline.execute()


def get_auth_code_data(code: str) -> Optional[AuthCodeData]:
    redis_client = get_client()

    code_key = AUTH_CODE_PREFIX + code

    auth_code_data_dict = redis_client.hgetall(code_key)
    if not auth_code_data_dict:
        return None

    return AuthCodeData(**auth_code_data_dict)


def remove_auth_code(code: str) -> None:
    redis_client = get_client()
    code_key = AUTH_CODE_PREFIX + code
    redis_client.delete(code_key)
