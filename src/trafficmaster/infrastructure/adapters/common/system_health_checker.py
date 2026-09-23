import asyncio
from typing import TYPE_CHECKING, Final, cast, override

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from trafficmaster.application.common.ports.system_health import SystemHealth, SystemHealthChecker
from trafficmaster.setup.config.asgi import ASGIConfig

if TYPE_CHECKING:
    from collections.abc import Awaitable


class InfrastructureSystemHealthChecker(SystemHealthChecker):
    def __init__(self, engine: AsyncEngine, redis_client: Redis, asgi_config: ASGIConfig) -> None:
        self._engine: Final[AsyncEngine] = engine
        self._redis_client: Final[Redis] = redis_client
        self._timeout: Final[float] = asgi_config.healthcheck_timeout_seconds

    @override
    async def check(self) -> SystemHealth:
        database_available, cache_available = await asyncio.gather(
            self._database_is_available(),
            self._cache_is_available(),
        )
        return SystemHealth(
            database_available=database_available,
            cache_available=cache_available,
        )

    async def _database_is_available(self) -> bool:
        try:
            async with asyncio.timeout(self._timeout), self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except (TimeoutError, SQLAlchemyError, OSError):
            return False
        return True

    async def _cache_is_available(self) -> bool:
        try:
            async with asyncio.timeout(self._timeout):
                await cast("Awaitable[bool]", self._redis_client.ping())
        except (TimeoutError, RedisError, OSError):
            return False
        return True
