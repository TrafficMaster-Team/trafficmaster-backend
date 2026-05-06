from dataclasses import dataclass
from typing import TYPE_CHECKING

from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.user import (
    NoPermissionToManageUserError,
    UserAlreadyExistsError,
)
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.raw_password import RawPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    email: str
    username: str
    password: str
    role: UserRole = UserRole.USER


class CreateUserCommandHandler:
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

    async def __call__(self, data: CreateUserCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()

        created_user: User = self._user_service.create_user(
            email=UserEmail(data.email),
            name=Username(data.username),
            role=data.role,
            raw_password=RawPassword(data.password),
        )

        if (await self._user_gateway.read_by_email(created_user.email)) is not None:
            msg = "User with this email already exists"
            raise UserAlreadyExistsError(msg)

        if not self._access_service.can_manage_user(created_user, current_user):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        await self._user_gateway.add(created_user)
        await self._transaction_manager.commit()
