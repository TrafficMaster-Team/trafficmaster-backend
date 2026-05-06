from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView


class ReadCurrentUserHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
    ) -> None:
        self._current_user_service = current_user_service

    async def __call__(self) -> ReadUserByIDView:
        user = await self._current_user_service.get_current_user()

        return ReadUserByIDView(
            id=user.id,
            name=str(user.name),
            email=str(user.email),
            role=user.role,
        )
