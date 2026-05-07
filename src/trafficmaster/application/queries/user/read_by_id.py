from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView
from trafficmaster.application.errors.user import UserNotFoundByIdError
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadByIdQuery:
    user_id: UUID


class ReadUserByIdQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_gateway: UserGateway,
        access_service: AccessService,
    ) -> None:
        self._access_service: Final[AccessService] = access_service
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_gateway: Final[UserGateway] = user_gateway

    async def __call__(self, data: ReadByIdQuery) -> ReadUserByIDView:

        user_id: UserID = UserID(data.user_id)

        user: User | None = await self._user_gateway.read_by_id(user_id)

        if user is None:
            msg = f"Can't find user with id {data.user_id}"
            raise UserNotFoundByIdError(msg)

        await self._user_gateway.read_by_id(user_id)

        return ReadUserByIDView(
            id=user_id,
            name=str(user.name),
            email=str(user.email),
            role=user.role,
        )
