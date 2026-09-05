from functools import lru_cache

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from trafficmaster.infrastructure.persistence.models.auth_sessions import map_auth_session_table
from trafficmaster.infrastructure.persistence.models.card_progress import map_card_progress_table
from trafficmaster.infrastructure.persistence.models.cards import map_cards_table
from trafficmaster.infrastructure.persistence.models.deck_configs import map_deck_configs_table
from trafficmaster.infrastructure.persistence.models.decks import map_decks_table
from trafficmaster.infrastructure.persistence.models.review_logs import map_review_logs_table
from trafficmaster.infrastructure.persistence.models.users import map_users_table
from trafficmaster.presentation.http.v1.common.auth_cookie import AuthCookieParams
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionHandler
from trafficmaster.presentation.http.v1.common.routes import healthcheck, index
from trafficmaster.presentation.http.v1.middlewares.auth_cookie import AuthCookieMiddleware
from trafficmaster.presentation.http.v1.middlewares.client_cache import ClientCacheMiddleware
from trafficmaster.presentation.http.v1.routes.auth import auth_router
from trafficmaster.presentation.http.v1.routes.card import card_router
from trafficmaster.presentation.http.v1.routes.card_progress import card_progress_router
from trafficmaster.presentation.http.v1.routes.deck import deck_router
from trafficmaster.presentation.http.v1.routes.deck_config import deck_config_router
from trafficmaster.presentation.http.v1.routes.user import user_router
from trafficmaster.setup.config.asgi import ASGIConfig
from trafficmaster.setup.config.settings import AppConfig


@lru_cache(maxsize=1)
def setup_configs() -> AppConfig:
    return AppConfig()


@lru_cache(maxsize=1)
def setup_map_configs() -> None:
    map_auth_session_table()
    map_card_progress_table()
    map_cards_table()
    map_decks_table()
    map_deck_configs_table()
    map_review_logs_table()
    map_users_table()


def setup_http_routes(app: FastAPI) -> None:
    app.include_router(index.router)
    app.include_router(healthcheck.router)
    router_v1: APIRouter = APIRouter(prefix="/v1")
    router_v1.include_router(auth_router)
    router_v1.include_router(user_router)
    router_v1.include_router(deck_router)
    router_v1.include_router(card_router)
    router_v1.include_router(deck_config_router)
    router_v1.include_router(card_progress_router)
    app.include_router(router_v1)


def setup_exc_handlers(app: FastAPI) -> None:
    exception_handler: ExceptionHandler = ExceptionHandler(app)
    exception_handler.setup_exception_handlers()


def setup_http_middlewares(app: FastAPI, api_config: ASGIConfig, cookie_params: AuthCookieParams) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://localhost:{api_config.port}",
            f"https://{api_config.host}:{api_config.port}",
            f"http://127.0.0.1:{api_config.port}",
            "http://127.0.0.1",
        ],
        allow_credentials=api_config.allow_credentials,
        allow_methods=api_config.allow_methods,
        allow_headers=api_config.allow_headers,
    )
    app.add_middleware(AuthCookieMiddleware, cookie_params=cookie_params)
    app.add_middleware(ClientCacheMiddleware)
