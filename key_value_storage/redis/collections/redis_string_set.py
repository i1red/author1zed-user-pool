import datetime
from typing import Final

from redis.client import Redis


EMPTY_VALUE: Final[str] = ""


class RedisStringSet:
    def __init__(
        self,
        redis_client: Redis,
        collection_prefix: str,
        ttl: datetime.timedelta | None = None,
    ) -> None:
        self._redis_client = redis_client
        self._collection_prefix = collection_prefix
        self._ttl = ttl

    def save(self, key: str) -> None:
        prefixed_key = self._add_key_prefix(key)

        self._redis_client.set(prefixed_key, EMPTY_VALUE)
        if self._ttl is not None:
            self._redis_client.expire(prefixed_key, time=self._ttl)

    def contains(self, key: str) -> bool:
        return self._redis_client.get(self._add_key_prefix(key)) is not None

    def remove(self, key: str) -> None:
        self._redis_client.delete(self._add_key_prefix(key))

    def _add_key_prefix(self, key: str) -> str:
        return f"{self._collection_prefix}:{key}"
