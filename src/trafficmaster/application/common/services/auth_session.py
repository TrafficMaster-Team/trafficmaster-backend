from multiprocessing.context import AuthenticationError
from typing import TYPE_CHECKING, Final

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.application.common.ports.auth.gateway import AuthSessionGateway
from trafficmaster.application.common.ports.auth.id_generator import AuthIDGenerator
from trafficmaster.application.common.ports.auth.session_timer import SessionTimer
from trafficmaster.application.common.ports.auth.transport import AuthSessionTransport
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from datetime import datetime


class AuthSessionService:
    def __init__(
        self,
        auth_session_id: AuthIDGenerator,
        auth_timer: SessionTimer,
        auth_gateway: AuthSessionGateway,
        transaction_manager: TransactionManager,
        auth_transport: AuthSessionTransport,
    ) -> None:
        self._auth_session_id: Final[AuthIDGenerator] = auth_session_id
        self._auth_timer: Final[SessionTimer] = auth_timer
        self._auth_gateway: Final[AuthSessionGateway] = auth_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._cached_session: AuthSession | None = None
        self._auth_transport = auth_transport

    async def create_session(self, user_id: UserID) -> None:

        auth_session_id = self._auth_session_id()
        expiration: datetime = self._auth_timer.auth_session_expired
        auth_session = AuthSession(
            id=auth_session_id,
            user_id=user_id,
            expiration=expiration,
        )
        try:
            await self._auth_gateway.add(auth_session)
            await self._transaction_manager.commit()
        except GatewayError as error:
            msg = "Authentification is currently unavailable"
            raise AuthenticationError(msg) from error

        self._auth_transport.deliver(auth_session)

    async def get_authenticated_user_id(self) -> UserID:

        session: AuthSession = await self.load_current_session()
        validated_session = await self.validate_and_extend_session(session)

        return validated_session.user_id

    async def invalidate_current_session(self) -> None:

        auth_session: AuthSession = self._auth_transport.extract_id()

        if auth_session is None:
            return

        self._auth_transport.remove_current()

        try:
            auth_session = await self._auth_gateway.read_by_id(auth_session.id)
        except GatewayError as error:
            msg = "Authentification is currently unavailable"
            raise AuthenticationError(msg) from error

        if auth_session is None:
            return

        try:
            await self._auth_gateway.delete(auth_session_id=auth_session.id)
            await self._transaction_manager.commit()
        except GatewayError as error:
            msg = "Authentification is currently unavailable"
            raise AuthenticationError(msg) from error

    async def invalidate_all_user_sessions(self, user_id: UserID) -> None:

        try:
            await self._auth_gateway.delete_all_for_user(user_id)
            await self._transaction_manager.commit()
        except GatewayError as error:
            msg = "Authentification is currently unavailable"
            raise AuthenticationError(msg) from error

    async def load_current_session(self) -> AuthSession:
        if self._cached_session:
            return self._cached_session

        auth_session_id = self._auth_transport.extract_id()
        if auth_session_id is None:
            msg = "Authentication failed"
            raise AuthenticationError(msg)

        try:
            auth_session = self._auth_gateway.read_by_id(auth_session_id)
        except GatewayError as error:
            msg = "Authentication failed."
            raise AuthenticationError(msg) from error

        if auth_session is None:
            msg = "Authentication failed."
            raise AuthenticationError(msg)

        self._cached_session = auth_session

        return self._cached_session

    async def validate_and_extend_session(self, auth_session: AuthSession) -> AuthSession:
        now = self._auth_timer.current_time
        original_expiration = auth_session.expiration
        if original_expiration <= now:
            msg = "Session expired"
            raise AuthenticationError(msg)

        if original_expiration - now > self._auth_timer.refresh_trigger_interval:
            return auth_session

        auth_session.expiration = self._auth_timer.auth_session_expired
        try:
            await self._auth_gateway.add(auth_session)
            await self._transaction_manager.commit()
        except GatewayError as error:
            msg = "Authentification failed."
            raise AuthenticationError(msg) from error

        auth_session.expiration = original_expiration

        self._cached_session = auth_session
        return auth_session
