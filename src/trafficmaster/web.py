from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.orm import clear_mappers

from trafficmaster.infrastructure.adapters.auth.cookie_params import CookieParams
from trafficmaster.infrastructure.adapters.auth.jwt_token_processor import JwtAlgorithm, JwtSecret
from trafficmaster.infrastructure.adapters.auth.timer_utc import AuthSessionRefreshThreshold, AuthSessionTtlMin
from trafficmaster.infrastructure.adapters.common.password_hasher_bcrypt import PasswordPepper
from trafficmaster.setup.bootstrap import setup_configs, setup_map_configs
from trafficmaster.setup.config.asgi import ASGIConfig
from trafficmaster.setup.config.database import PostgresConfig, SQLAlchemyConfig
from trafficmaster.setup.config.redis import RedisConfig
from trafficmaster.setup.ioc import setup_providers

if TYPE_CHECKING:
    from trafficmaster.setup.config.settings import AppConfig


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    clear_mappers()
    await app.state.dishka_container.close()


def create_fastapi_app() -> FastAPI:

    configs: AppConfig = setup_configs()
    setup_map_configs()

    app: FastAPI = FastAPI(lifespan=lifespan, version="1.0.0", debug=configs.asgi.fastapi_debug)

    context = {
        ASGIConfig: configs.asgi,
        RedisConfig: configs.redis,
        SQLAlchemyConfig: configs.sqlalchemy,
        PostgresConfig: configs.postgres,
        JwtSecret: configs.security.auth.jwt_secret,
        PasswordPepper: configs.security.password.pepper,
        JwtAlgorithm: configs.security.auth.jwt_algorithm,
        AuthSessionTtlMin: configs.security.auth.session_ttl_min,
        AuthSessionRefreshThreshold: configs.security.auth.session_refresh_threshold,
        CookieParams: CookieParams(secure=configs.security.cookies.secure),
    }

    container: AsyncContainer = make_async_container(*setup_providers(), context=context)
    setup_dishka(container, app)
    return app
