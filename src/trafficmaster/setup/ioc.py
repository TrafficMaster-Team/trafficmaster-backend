from typing import Final

from dishka import Provider, Scope
from starlette.requests import Request

from trafficmaster.application.auth.auth_model import AuthSession  # noqa: F401  # required for mapper side-effects
from trafficmaster.application.common.ports.access_revoker import AccessRevoker
from trafficmaster.application.common.ports.auth.gateway import AuthSessionGateway
from trafficmaster.application.common.ports.auth.id_generator import AuthIDGenerator
from trafficmaster.application.common.ports.auth.session_timer import SessionTimer
from trafficmaster.application.common.ports.auth.transport import AuthSessionTransport
from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.clock import Clock
from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.identity_provider import IdentityProvider
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.auth_session import AuthSessionService
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.domain.card.ports.card_id_generator import CardIDGenerator
from trafficmaster.domain.card.services.card_service import CardService
from trafficmaster.domain.card_progress.ports.card_progress_id_generator import CardProgressIDGenerator
from trafficmaster.domain.card_progress.ports.review_id_generator import ReviewIDGenerator
from trafficmaster.domain.card_progress.services.card_progress_service import CardProgressService
from trafficmaster.domain.deck.ports.deck_config_id_generator import DeckConfigIDGenerator
from trafficmaster.domain.deck.ports.deck_id_generator import DeckIDGenerator
from trafficmaster.domain.deck.services.deck_config_service import DeckConfigService
from trafficmaster.domain.deck.services.deck_service import DeckService
from trafficmaster.domain.user.ports.id_generator import UserIDGenerator
from trafficmaster.domain.user.ports.password_hasher import PasswordHasher
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.infrastructure.adapters.auth.access_revoker import AuthSessionAccessRevoker
from trafficmaster.infrastructure.adapters.auth.cookie_params import CookieParams
from trafficmaster.infrastructure.adapters.auth.identity_provider import AuthSessionIdentityProvider
from trafficmaster.infrastructure.adapters.auth.jwt_auth_session_transport import JwtAuthSessionTransport
from trafficmaster.infrastructure.adapters.auth.jwt_token_processor import (
    JwtAccessTokenProcessor,
    JwtAlgorithm,
    JwtSecret,
)
from trafficmaster.infrastructure.adapters.auth.secrets_auth_session_id_generator import SecretsAuthSessionIdGenerator
from trafficmaster.infrastructure.adapters.auth.timer_utc import (
    AuthSessionRefreshThreshold,
    AuthSessionTtlMin,
    UtcAuthSessionTimer,
)
from trafficmaster.infrastructure.adapters.common.clock_utc import UtcClock
from trafficmaster.infrastructure.adapters.common.password_hasher_bcrypt import BcryptPasswordHasher, PasswordPepper
from trafficmaster.infrastructure.adapters.common.uuid4_card_id_generator import UUID4CardIdGenerator
from trafficmaster.infrastructure.adapters.common.uuid4_card_progress_id_generator import UUID4CardProgressIdGenerator
from trafficmaster.infrastructure.adapters.common.uuid4_deck_config_id_generator import UUID4DeckConfigIdGenerator
from trafficmaster.infrastructure.adapters.common.uuid4_deck_id_generator import UUID4DeckIdGenerator
from trafficmaster.infrastructure.adapters.common.uuid4_review_id_generator import UUID4ReviewIdGenerator
from trafficmaster.infrastructure.adapters.common.uuid4_user_id_generator import UUID4UserIdGenerator
from trafficmaster.infrastructure.adapters.persistence.alchemy_auth_session_gateway import AlchemyAuthSessionGateway
from trafficmaster.infrastructure.adapters.persistence.alchemy_card_gateway import AlchemyCardGateway
from trafficmaster.infrastructure.adapters.persistence.alchemy_card_progress_gateway import AlchemyCardProgressGateway
from trafficmaster.infrastructure.adapters.persistence.alchemy_deck_config_gateway import AlchemyDeckConfigGateway
from trafficmaster.infrastructure.adapters.persistence.alchemy_deck_gateway import AlchemyDeckGateway
from trafficmaster.infrastructure.adapters.persistence.alchemy_review_log_gateway import AlchemyReviewLogGateway
from trafficmaster.infrastructure.adapters.persistence.alchemy_transaction_manager import SqlAlchemyTransactionManager
from trafficmaster.infrastructure.adapters.persistence.alchemy_user_gateway import AlchemyUserGateway
from trafficmaster.infrastructure.adapters.persistence.cached_deck_config_gateway import CachedDeckConfigGateway
from trafficmaster.infrastructure.adapters.persistence.cached_deck_gateway import CachedDeckGateway
from trafficmaster.infrastructure.adapters.persistence.cached_user_gateway import CachedUserGateway
from trafficmaster.infrastructure.cache.cache_store import CacheStore
from trafficmaster.infrastructure.cache.provider import get_redis, get_redis_pool
from trafficmaster.infrastructure.cache.redis_cache_store import RedisCacheStore
from trafficmaster.infrastructure.persistence.provider import get_engine, get_session, get_sessionmaker
from trafficmaster.setup.config.database import PostgresConfig, SQLAlchemyConfig
from trafficmaster.setup.config.redis import RedisConfig


def configs_provider() -> Provider:
    provider = Provider(scope=Scope.APP)
    provider.from_context(provides=PostgresConfig)
    provider.from_context(provides=RedisConfig)
    provider.from_context(provides=SQLAlchemyConfig)
    provider.from_context(provides=JwtSecret)
    provider.from_context(provides=JwtAlgorithm)
    provider.from_context(provides=PasswordPepper)
    provider.from_context(provides=AuthSessionTtlMin)
    provider.from_context(provides=AuthSessionRefreshThreshold)
    provider.from_context(provides=CookieParams)
    return provider


def db_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    provider.provide(source=get_engine, scope=Scope.APP)
    provider.provide(source=get_sessionmaker, scope=Scope.APP)
    provider.provide(source=get_session)
    provider.provide(source=SqlAlchemyTransactionManager, provides=TransactionManager)
    provider.provide(source=AlchemyUserGateway, provides=UserGateway)
    provider.provide(source=AlchemyDeckGateway, provides=DeckGateway)
    provider.provide(source=AlchemyDeckConfigGateway, provides=DeckConfigGateway)
    provider.provide(source=AlchemyCardGateway, provides=CardGateway)
    provider.provide(source=AlchemyCardProgressGateway, provides=CardProgressGateway)
    provider.provide(source=AlchemyReviewLogGateway, provides=ReviewLogGateway)
    provider.provide(source=AlchemyAuthSessionGateway, provides=AuthSessionGateway)
    return provider


def cache_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    provider.provide(source=get_redis_pool, scope=Scope.APP)
    provider.provide(source=get_redis)
    provider.provide(source=RedisCacheStore, provides=CacheStore)
    provider.decorate(source=CachedUserGateway, provides=UserGateway)
    provider.decorate(source=CachedDeckGateway, provides=DeckGateway)
    provider.decorate(source=CachedDeckConfigGateway, provides=DeckConfigGateway)
    return provider


def domain_ports_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.APP)
    provider.provide(source=UtcClock, provides=Clock)
    provider.provide(source=BcryptPasswordHasher, provides=PasswordHasher)
    provider.provide(source=UUID4UserIdGenerator, provides=UserIDGenerator)
    provider.provide(source=UUID4DeckIdGenerator, provides=DeckIDGenerator)
    provider.provide(source=UUID4DeckConfigIdGenerator, provides=DeckConfigIDGenerator)
    provider.provide(source=UUID4CardIdGenerator, provides=CardIDGenerator)
    provider.provide(source=UUID4CardProgressIdGenerator, provides=CardProgressIDGenerator)
    provider.provide(source=UUID4ReviewIdGenerator, provides=ReviewIDGenerator)
    provider.provide_all(
        UserService,
        AccessService,
        CardService,
        DeckService,
        DeckConfigService,
        CardProgressService,
    )
    return provider


def auth_ports_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.from_context(provides=Request, scope=Scope.REQUEST)
    provider.provide_all(CurrentUserService, JwtAccessTokenProcessor)
    provider.provide(source=UtcAuthSessionTimer, provides=SessionTimer)
    provider.provide(source=SecretsAuthSessionIdGenerator, provides=AuthIDGenerator)
    provider.provide(source=AuthSessionAccessRevoker, provides=AccessRevoker)
    provider.provide(source=AuthSessionIdentityProvider, provides=IdentityProvider)
    provider.provide(source=AuthSessionService)
    provider.provide(source=JwtAuthSessionTransport, provides=AuthSessionTransport)
    return provider
