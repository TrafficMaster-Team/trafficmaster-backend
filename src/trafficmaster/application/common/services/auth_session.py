from multiprocessing.context import AuthenticationError
from typing import TYPE_CHECKING, Final

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.application.common.ports.auth.gateway import AuthSessionGateway
from trafficmaster.application.common.ports.auth.id_generator import AuthIDGenerator
from trafficmaster.application.common.ports.auth.session_timer import SessionTimer
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
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
    ) -> None:
        self._auth_session_id: Final[AuthIDGenerator] = auth_session_id
        self._auth_timer: Final[SessionTimer] = auth_timer
        self._auth_gateway: Final[AuthSessionGateway] = auth_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._cached_session: AuthSession | None = None

    async def create_session(self, user_id: UserID) -> AuthSession:

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
        except KeyError as error:  # IMPLEMENT REPOERROR IN THE FUTURE
            msg = "Authentification is currently unavailable"
            raise AuthenticationError(msg) from error
        return auth_session

    async def get_authenticated_user_id(self, session_id: AuthSession) -> UserID: ...
