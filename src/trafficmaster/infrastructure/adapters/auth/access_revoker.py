from typing import Final, override

from trafficmaster.application.common.ports.access_revoker import AccessRevoker
from trafficmaster.application.common.services.auth_session import AuthSessionService
from trafficmaster.domain.user.values.user_id import UserID


class AuthSessionAccessRevoker(AccessRevoker):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service: Final[AuthSessionService] = auth_session_service

    @override
    async def remove_all_user_access(self, user: UserID) -> None:
        await self._auth_session_service.invalidate_all_user_sessions(user)
