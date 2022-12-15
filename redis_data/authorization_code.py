import dataclasses
import datetime
from typing import Final

from redis_data.client import get_client


AUTH_CODE_PREFIX: Final[str] = "auth_code:"


@dataclasses.dataclass
class AuthCodeData:
    client_id: str
    user_id: str


def save_auth_code_data(code: str, auth_code_data: AuthCodeData) -> None:
    redis_client = get_client()

    code_key = AUTH_CODE_PREFIX + code

    pipeline = redis_client.pipeline()

    pipeline.multi()

    for key, value in dataclasses.asdict(auth_code_data).items():
        pipeline.hset(code_key, key, value)

    pipeline.expire(code_key, time=datetime.timedelta(minutes=10))

    pipeline.execute()
