import dataclasses
import datetime
from typing import TypeVar, Type

from redis.client import Redis

from author1zd.key_value_storage.abstract.collections.string_to_dataclass_map import StringToDataclassMap

TObject = TypeVar("TObject")


class RedisStringToDataclassMap(StringToDataclassMap[TObject]):
    def __init__(
        self,
        redis_client: Redis,
        object_type: Type[TObject],
        collection_prefix: str,
        ttl: datetime.timedelta | None = None,
    ) -> None:
        self._redis_client = redis_client
        self._object_type = object_type
        self._collection_prefix = collection_prefix
        self._ttl = ttl

    def save(self, key: str, obj: TObject) -> None:
        prefixed_key = self._add_key_prefix(key)

        pipeline = self._redis_client.pipeline()
        pipeline.multi()

        for key, value in dataclasses.asdict(obj).items():
            pipeline.hset(prefixed_key, key, value)

        if self._ttl is not None:
            pipeline.expire(prefixed_key, time=self._ttl)

        pipeline.execute()

    def get(self, key: str) -> TObject | None:
        prefixed_key = self._add_key_prefix(key)

        obj_dict = self._redis_client.hgetall(prefixed_key)
        if not obj_dict:
            return None

        return self._object_type(**obj_dict)

    def remove(self, key: str) -> None:
        self._redis_client.delete(self._add_key_prefix(key))

    def _add_key_prefix(self, key: str) -> str:
        return f"{self._collection_prefix}:{key}"
