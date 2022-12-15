import dataclasses
import datetime
from typing import Optional, Final

from redis.exceptions import WatchError

from redis_data.client import get_client


STATE_KEY_PREFIX: Final[str] = "state:"


class StateException(Exception):
    pass


@dataclasses.dataclass
class StateData:
    client_id: str
    redirect_uri: str


def save_state_data(state: str, state_data: StateData) -> None:
    redis_client = get_client()
    state_key = STATE_KEY_PREFIX + state

    pipeline = redis_client.pipeline()

    try:
        pipeline.watch(state_key)

        state_data_dict = pipeline.hgetall(state_key)

        if state_data_dict:
            pipeline.unwatch()
            raise StateException("State already exits")

        pipeline.multi()

        for key, value in dataclasses.asdict(state_data).items():
            pipeline.hset(state_key, key, value)

        pipeline.expire(state_key, time=datetime.timedelta(minutes=10))

        pipeline.execute()
    except WatchError:
        raise StateException("Simultaneous attempt to change state")


def get_state_data(state: str) -> Optional[StateData]:
    redis_client = get_client()
    state_key = STATE_KEY_PREFIX + state

    state_data_dict = redis_client.hgetall(state_key)
    if not state_data_dict:
        return None

    return StateData(**state_data_dict)
