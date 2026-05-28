from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from sqlalchemy.orm import clear_mappers

from trafficmaster.setup.bootstrap import setup_configs, setup_map_configs

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
    return app
