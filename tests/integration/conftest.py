import os
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

_POSTGRES_DB = "trafficmaster"
_POSTGRES_USER = "postgres"
_POSTGRES_PASSWORD = "postgres"  # noqa: S105
_REDIS_PASSWORD = "secret"  # noqa: S105


@pytest.fixture(scope="session")
def _containers() -> Iterator[tuple[PostgresContainer, RedisContainer]]:
    postgres = PostgresContainer(
        "postgres:16-alpine",
        username=_POSTGRES_USER,
        password=_POSTGRES_PASSWORD,
        dbname=_POSTGRES_DB,
    )
    redis = RedisContainer("redis:7-alpine", password=_REDIS_PASSWORD)
    with postgres, redis:
        yield postgres, redis


def _apply_env(postgres: PostgresContainer, redis: RedisContainer) -> None:
    env = {
        "POSTGRES_USER": _POSTGRES_USER,
        "POSTGRES_PASSWORD": _POSTGRES_PASSWORD,
        "POSTGRES_DB": _POSTGRES_DB,
        "POSTGRES_DRIVER": "asyncpg",
        "POSTGRES_HOST": postgres.get_container_host_ip(),
        "POSTGRES_PORT": str(postgres.get_exposed_port(5432)),
        "DB_POOL_PRE_PING": "True",
        "DB_POOL_RECYCLE": "3600",
        "DB_POOL_SIZE": "10",
        "DB_POOL_MAX_OVERFLOW": "10",
        "DB_ECHO": "False",
        "DB_AUTO_FLUSH": "False",
        "DB_EXPIRE_ON_COMMIT": "False",
        "REDIS_HOST": redis.get_container_host_ip(),
        "REDIS_PORT": str(redis.get_exposed_port(6379)),
        "REDIS_PASSWORD": _REDIS_PASSWORD,
        "REDIS_CACHE_DB": "0",
        "REDIS_MAX_CONNECTIONS": "20",
        "JWT_SECRET": "integration-test-secret-key-0123456789",
        "JWT_ALGORITHM": "HS256",
        "PEPPER": "integration-test-pepper",
        "SESSION_TTL_MIN": "60",
        "SESSION_REFRESH_THRESHOLD": "0.2",
        "SECURE": "0",
        "UVICORN_HOST": "127.0.0.1",
        "UVICORN_PORT": "8080",
    }
    os.environ.update(env)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app(_containers: tuple[PostgresContainer, RedisContainer]) -> AsyncIterator[object]:
    postgres, redis = _containers
    _apply_env(postgres, redis)

    # Build configs/mappers fresh against the container environment.
    from trafficmaster.setup.bootstrap import setup_configs, setup_map_configs  # noqa: PLC0415

    setup_configs.cache_clear()
    setup_map_configs.cache_clear()

    from trafficmaster.infrastructure.persistence.models.base import metadata  # noqa: PLC0415
    from trafficmaster.web import create_fastapi_app  # noqa: PLC0415

    application = create_fastapi_app()
    container = application.state.dishka_container

    engine = await container.get(AsyncEngine)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield application

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await container.close()


@pytest_asyncio.fixture(loop_scope="session")
async def client(app: object) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
