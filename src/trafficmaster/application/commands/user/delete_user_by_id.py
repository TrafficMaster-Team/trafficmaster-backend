from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteUserByIdCommand:
    user_id: UUID


class DeleteUserByIdCommandHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        access_service: AccessService,
        user_gateway: UserGateway,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_service: Final[UserService] = user_service
        self._access_service: Final[AccessService] = access_service
        self._user_gateway: Final[UserGateway] = user_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager

    async def __call__(self, data: DeleteUserByIdCommand) -> None:

        current_user = await self._current_user_service.get_current_user()

        user_for_delete: User | None = await self._user_gateway.read_by_id(UserID(data.user_id))

        if user_for_delete is None:
            msg = f"Can't find user with id {data.user_id}"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(current_user, user_for_delete):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        await self._user_gateway.delete_by_id(UserID(data.user_id))
        await self._transaction_manager.commit()
