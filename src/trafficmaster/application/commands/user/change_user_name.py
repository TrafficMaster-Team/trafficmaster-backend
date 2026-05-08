from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.domain.user.values.user_name import Username

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeUserNameCommand:
    user_id: UUID
    username: str


class ChangeUserNameCommandHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_gateway: UserGateway,
        access_service: AccessService,
        transaction_manager: TransactionManager,
    ) -> None:
        self._user_service = user_service
        self._current_user_service = current_user_service
        self._user_gateway = user_gateway
        self._access_service = access_service
        self._transaction_manager = transaction_manager

    async def __call__(self, data: ChangeUserNameCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()

        user_for_update_name: User | None = await self._user_gateway.read_by_id(UserID(data.user_id))

        if user_for_update_name is None:
            msg = f"Can't find user with id {data.user_id}"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(current_user, user_for_update_name):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        validated_name = Username(data.username)

        self._user_service.change_name(user=user_for_update_name, name=validated_name)
        await self._transaction_manager.commit()
