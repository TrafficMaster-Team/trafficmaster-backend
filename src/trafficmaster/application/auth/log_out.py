from typing import Final

from trafficmaster.application.common.services.auth_session import AuthSessionService


class LogOutHandler:
    def __init__(
        self,
        auth_service: AuthSessionService,
    ) -> None:
        self._auth_service: Final[AuthSessionService] = auth_service

    async def __call__(self) -> None:
        await self._auth_service.invalidate_current_session()
