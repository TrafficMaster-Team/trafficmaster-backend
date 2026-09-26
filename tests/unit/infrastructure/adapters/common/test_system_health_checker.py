import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from trafficmaster.infrastructure.adapters.common.system_health_checker import InfrastructureSystemHealthChecker
from trafficmaster.setup.config.asgi import ASGIConfig

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncEngine


class ConnectionStub:
    def __init__(self, execute: Callable[[], Awaitable[None]]) -> None:
        self._execute = execute

    async def execute(self, _statement: object) -> None:
        await self._execute()


class ConnectionContextStub:
    def __init__(self, connection: ConnectionStub) -> None:
        self._connection = connection

    async def __aenter__(self) -> ConnectionStub:
        return self._connection

    async def __aexit__(self, *_args: object) -> None:
        return None


class EngineStub:
    def __init__(self, execute: Callable[[], Awaitable[None]]) -> None:
        self._execute = execute

    def connect(self) -> ConnectionContextStub:
        return ConnectionContextStub(ConnectionStub(self._execute))


class RedisStub:
    def __init__(self, ping: Callable[[], Awaitable[bool]]) -> None:
        self._ping = ping

    async def ping(self) -> bool:
        return await self._ping()


async def succeed() -> None:
    return None


async def ping_succeeds() -> bool:
    return True


def create_checker(
    *,
    execute: Callable[[], Awaitable[None]] = succeed,
    ping: Callable[[], Awaitable[bool]] = ping_succeeds,
    timeout: float = 1.0,
) -> InfrastructureSystemHealthChecker:
    config = ASGIConfig.model_validate({"HEALTHCHECK_TIMEOUT_SECONDS": timeout})
    return InfrastructureSystemHealthChecker(
        engine=cast("AsyncEngine", EngineStub(execute)),
        redis_client=cast("Redis[Any]", RedisStub(ping)),
        asgi_config=config,
    )


async def test_check_reports_all_dependencies_available() -> None:
    health = await create_checker().check()

    assert health.database_available is True
    assert health.cache_available is True
    assert health.ready is True


async def test_check_reports_database_failure_as_not_ready() -> None:
    async def fail_database() -> None:
        raise SQLAlchemyError

    health = await create_checker(execute=fail_database).check()

    assert health.database_available is False
    assert health.cache_available is True
    assert health.ready is False


async def test_check_reports_cache_failure_as_degraded() -> None:
    async def fail_cache() -> bool:
        raise RedisError

    health = await create_checker(ping=fail_cache).check()

    assert health.database_available is True
    assert health.cache_available is False
    assert health.ready is True


async def test_check_times_out_each_dependency() -> None:
    async def hang() -> None:
        await asyncio.sleep(1)

    async def ping_hangs() -> bool:
        await asyncio.sleep(1)
        return True

    health = await create_checker(execute=hang, ping=ping_hangs, timeout=0.001).check()

    assert health.database_available is False
    assert health.cache_available is False
