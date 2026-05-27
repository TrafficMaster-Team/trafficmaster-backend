from collections.abc import Iterable
from typing import Final

from dishka import Provider, Scope
from starlette.requests import Request

from trafficmaster.application.auth.auth_model import AuthSession  # noqa: F401  # required for mapper side-effects
from trafficmaster.application.auth.log_in import LogInHandler
from trafficmaster.application.auth.log_out import LogOutHandler
from trafficmaster.application.auth.read_current_user import ReadCurrentUserHandler
from trafficmaster.application.auth.sign_up import SignUpHandler
from trafficmaster.application.commands.card.add_tag import AddTagCommandHandler
from trafficmaster.application.commands.card.change_answer import ChangeAnswerCommandHandler
from trafficmaster.application.commands.card.change_deck import ChangeDeckCommandHandler
from trafficmaster.application.commands.card.change_image_path import ChangeImagePathCommandHandler
from trafficmaster.application.commands.card.change_question import ChangeQuestionCommandHandler
from trafficmaster.application.commands.card.create_card import CreateCardCommandHandler
from trafficmaster.application.commands.card.delete_card import DeleteCardCommandHandler
from trafficmaster.application.commands.card.remove_tag import RemoveTagCommandHandler
from trafficmaster.application.commands.card_progress.reset_card_progress import ResetCardProgressCommandHandler
from trafficmaster.application.commands.card_progress.review_card import ReviewCardCommandHandler
from trafficmaster.application.commands.deck.assign_deck_config import AssignDeckConfigCommandHandler
from trafficmaster.application.commands.deck.change_description import ChangeDescriptionCommandHandler
from trafficmaster.application.commands.deck.change_privacy import ChangePrivacyCommandHandler
from trafficmaster.application.commands.deck.change_title import ChangeTitleCommandHandler
from trafficmaster.application.commands.deck.copy_deck import CopyDeckCommandHandler
from trafficmaster.application.commands.deck.create_deck import CreateDeckCommandHandler
from trafficmaster.application.commands.deck.delete_deck import DeleteDeckCommandHandler
from trafficmaster.application.commands.deck_config.change_advanced import ChangeAdvancedCommandHandler
from trafficmaster.application.commands.deck_config.change_config_name import ChangeConfigNameCommandHandler
from trafficmaster.application.commands.deck_config.change_daily_limits import ChangeDailyLimitsCommandHandler
from trafficmaster.application.commands.deck_config.change_lapses import ChangeLapsesCommandHandler
from trafficmaster.application.commands.deck_config.change_new_cards import ChangeNewCardsCommandHandler
from trafficmaster.application.commands.deck_config.create_deck_config import CreateDeckConfigCommandHandler
from trafficmaster.application.commands.deck_config.delete_deck_config import DeleteDeckConfigCommandHandler
from trafficmaster.application.commands.user.activate_user import ActivateUserCommandHandler
from trafficmaster.application.commands.user.change_user_email import ChangeUserEmailCommandHandler
from trafficmaster.application.commands.user.change_user_name import ChangeUserNameCommandHandler
from trafficmaster.application.commands.user.change_user_password import ChangeUserPasswordCommandHandler
from trafficmaster.application.commands.user.create_user import CreateUserCommandHandler
from trafficmaster.application.commands.user.delete_user_by_id import DeleteUserByIdCommandHandler
from trafficmaster.application.commands.user.grant_admin_by_id import GrantAdminByIdCommandHandler
from trafficmaster.application.commands.user.revoke_admin_by_id import RevokeAdminByIdCommandHandler
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
from trafficmaster.application.queries.card.read_all_cards import ReadAllCardsQueryHandler
from trafficmaster.application.queries.card.read_by_id import ReadCardByIdQueryHandler
from trafficmaster.application.queries.card_progress.preview_review_intervals import PreviewReviewIntervalsQueryHandler
from trafficmaster.application.queries.card_progress.read_card_progress import ReadCardProgressQueryHandler
from trafficmaster.application.queries.card_progress.read_deck_stats import ReadDeckStatsQueryHandler
from trafficmaster.application.queries.card_progress.read_review_log_by_card import ReadReviewLogByCardQueryHandler
from trafficmaster.application.queries.card_progress.read_review_log_by_user import ReadReviewLogByUserQueryHandler
from trafficmaster.application.queries.card_progress.read_review_queue import ReadReviewQueueQueryHandler
from trafficmaster.application.queries.deck.read_by_id import ReadDeckByIdQueryHandler
from trafficmaster.application.queries.deck.read_decks_by_user_id import ReadDecksByUserIdQueryHandler
from trafficmaster.application.queries.deck.read_public_decks import ReadPublicDecksQueryHandler
from trafficmaster.application.queries.deck_config.read_by_id import ReadDeckConfigByIdQueryHandler
from trafficmaster.application.queries.deck_config.read_by_user_id import ReadDeckConfigsByUserIdQueryHandler
from trafficmaster.application.queries.user.read_aggregate_stats import ReadUserAggregateStatsQueryHandler
from trafficmaster.application.queries.user.read_all_users import ReadAllUsersQueryHandler
from trafficmaster.application.queries.user.read_by_id import ReadUserByIdQueryHandler
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


def gateway_ports_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(source=SqlAlchemyTransactionManager, provides=TransactionManager)
    provider.provide(source=AlchemyUserGateway, provides=UserGateway)
    provider.provide(source=AlchemyDeckGateway, provides=DeckGateway)
    provider.provide(source=AlchemyDeckConfigGateway, provides=DeckConfigGateway)
    provider.provide(source=AlchemyCardGateway, provides=CardGateway)
    provider.provide(source=AlchemyCardProgressGateway, provides=CardProgressGateway)
    provider.provide(source=AlchemyReviewLogGateway, provides=ReviewLogGateway)
    provider.provide(source=AlchemyAuthSessionGateway, provides=AuthSessionGateway)
    return provider


def auth_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        SignUpHandler,
        LogInHandler,
        LogOutHandler,
        ReadCurrentUserHandler,
    )
    return provider


def user_command_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        CreateUserCommandHandler,
        ActivateUserCommandHandler,
        ChangeUserNameCommandHandler,
        ChangeUserEmailCommandHandler,
        ChangeUserPasswordCommandHandler,
        DeleteUserByIdCommandHandler,
        GrantAdminByIdCommandHandler,
        RevokeAdminByIdCommandHandler,
    )
    return provider


def deck_command_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        CreateDeckCommandHandler,
        DeleteDeckCommandHandler,
        CopyDeckCommandHandler,
        ChangeTitleCommandHandler,
        ChangeDescriptionCommandHandler,
        ChangePrivacyCommandHandler,
        AssignDeckConfigCommandHandler,
    )
    return provider


def deck_config_command_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        CreateDeckConfigCommandHandler,
        DeleteDeckConfigCommandHandler,
        ChangeConfigNameCommandHandler,
        ChangeAdvancedCommandHandler,
        ChangeDailyLimitsCommandHandler,
        ChangeLapsesCommandHandler,
        ChangeNewCardsCommandHandler,
    )
    return provider


def card_command_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        CreateCardCommandHandler,
        DeleteCardCommandHandler,
        ChangeQuestionCommandHandler,
        ChangeAnswerCommandHandler,
        ChangeImagePathCommandHandler,
        ChangeDeckCommandHandler,
        AddTagCommandHandler,
        RemoveTagCommandHandler,
    )
    return provider


def card_progress_command_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        ReviewCardCommandHandler,
        ResetCardProgressCommandHandler,
    )
    return provider


def user_query_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        ReadUserByIdQueryHandler,
        ReadAllUsersQueryHandler,
        ReadUserAggregateStatsQueryHandler,
    )
    return provider


def deck_query_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        ReadDeckByIdQueryHandler,
        ReadDecksByUserIdQueryHandler,
        ReadPublicDecksQueryHandler,
    )
    return provider


def deck_config_query_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        ReadDeckConfigByIdQueryHandler,
        ReadDeckConfigsByUserIdQueryHandler,
    )
    return provider


def card_query_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        ReadCardByIdQueryHandler,
        ReadAllCardsQueryHandler,
    )
    return provider


def card_progress_query_handlers_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        ReadCardProgressQueryHandler,
        ReadReviewQueueQueryHandler,
        ReadReviewLogByCardQueryHandler,
        ReadReviewLogByUserQueryHandler,
        ReadDeckStatsQueryHandler,
        PreviewReviewIntervalsQueryHandler,
    )
    return provider


def setup_providers() -> Iterable[Provider]:
    return (
        configs_provider(),
        db_provider(),
        cache_provider(),
        domain_ports_provider(),
        auth_ports_provider(),
        gateway_ports_provider(),
        auth_handlers_provider(),
        user_command_handlers_provider(),
        deck_command_handlers_provider(),
        deck_config_command_handlers_provider(),
        card_command_handlers_provider(),
        card_progress_command_handlers_provider(),
        user_query_handlers_provider(),
        deck_query_handlers_provider(),
        deck_config_query_handlers_provider(),
        card_query_handlers_provider(),
        card_progress_query_handlers_provider(),
    )
