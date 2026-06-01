"""Factories producing raw settings dicts keyed by their env-var aliases.

The config models use field aliases (e.g. ``POSTGRES_USER``) and are validated
by alias, so factory dicts mirror what ``Model(**os.environ)`` would receive.
"""

from typing import Any


def create_postgres_settings_data(
    user: str = "postgres",
    password: str = "postgres",  # noqa: S107
    host: str = "localhost",
    port: int = 5432,
    db: str = "trafficmaster",
    driver: str = "asyncpg",
) -> dict[str, Any]:
    return {
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": password,
        "POSTGRES_HOST": host,
        "POSTGRES_PORT": port,
        "POSTGRES_DB": db,
        "POSTGRES_DRIVER": driver,
    }


def create_sqlalchemy_settings_data(
    *,
    pool_pre_ping: bool = True,
    pool_size: int = 10,
    pool_recycle: int = 3600,
    max_overflow: int = 10,
    echo: bool = False,
    auto_flush: bool = False,
    expire_on_commit: bool = False,
) -> dict[str, Any]:
    return {
        "DB_POOL_PRE_PING": pool_pre_ping,
        "DB_POOL_SIZE": pool_size,
        "DB_POOL_RECYCLE": pool_recycle,
        "DB_POOL_MAX_OVERFLOW": max_overflow,
        "DB_ECHO": echo,
        "DB_AUTO_FLUSH": auto_flush,
        "DB_EXPIRE_ON_COMMIT": expire_on_commit,
    }


def create_redis_settings_data(
    host: str = "localhost",
    port: int = 6379,
    max_connections: int = 10,
    cache_db: int = 0,
    password: str = "redis",  # noqa: S107
) -> dict[str, Any]:
    return {
        "REDIS_HOST": host,
        "REDIS_PORT": port,
        "REDIS_MAX_CONNECTIONS": max_connections,
        "REDIS_CACHE_DB": cache_db,
        "REDIS_PASSWORD": password,
    }


def create_auth_settings_data(
    jwt_secret: str = "super-secret",  # noqa: S107
    jwt_algorithm: str = "HS256",
    session_ttl_min: str = "30",
    session_refresh_threshold: float = 0.5,
) -> dict[str, Any]:
    return {
        "JWT_SECRET": jwt_secret,
        "JWT_ALGORITHM": jwt_algorithm,
        "SESSION_TTL_MIN": session_ttl_min,
        "SESSION_REFRESH_THRESHOLD": session_refresh_threshold,
    }


def create_asgi_settings_data(**overrides: Any) -> dict[str, Any]:  # noqa: ANN401
    data: dict[str, Any] = {
        "UVICORN_HOST": "0.0.0.0",  # noqa: S104
        "UVICORN_PORT": 8000,
        "FASTAPI_DEBUG": True,
        "FASTAPI_ALLOW_CREDENTIALS": False,
    }
    data.update(overrides)
    return data
