from typing import Final, cast, override

from redis.asyncio import Redis
from redis.exceptions import RedisError

from trafficmaster.infrastructure.cache.cache_store import CacheStore, CacheStoreError


class RedisCacheStore(CacheStore):
    def __init__(self, redis_client: Redis) -> None:
        self._redis_client: Final[Redis] = redis_client

    @override
    async def get(self, name: str) -> bytes | None:
        try:
            return cast("bytes | None", await self._redis_client.get(name=name))
        except RedisError as error:
            raise CacheStoreError(str(error)) from error

    @override
    async def set(self, name: str, value: bytes, ttl: int) -> None:
        try:
            await self._redis_client.set(name=name, value=value, ex=ttl)
        except RedisError as error:
            raise CacheStoreError(str(error)) from error

    @override
    async def delete(self, name: str) -> None:
        try:
            await self._redis_client.delete(name)
        except RedisError as error:
            raise CacheStoreError(str(error)) from error
