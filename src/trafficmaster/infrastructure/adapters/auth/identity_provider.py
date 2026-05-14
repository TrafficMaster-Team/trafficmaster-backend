from typing import Final, override

from trafficmaster.application.common.ports.identity_provider import IdentityProvider
from trafficmaster.application.common.services.auth_session import AuthSessionService
from trafficmaster.domain.user.values.user_id import UserID


class AuthSessionIdentityProvider(IdentityProvider):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service: Final[AuthSessionService] = auth_session_service

    @override
    async def get_current_user_id(self) -> UserID:
        return await self._auth_session_service.get_authenticated_user_id()
