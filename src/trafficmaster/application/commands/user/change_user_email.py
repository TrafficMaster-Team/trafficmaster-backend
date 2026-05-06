from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.user import (
    EmailAlreadyExistsError,
    NoPermissionToManageUserError,
    UserNotFoundByEmailError,
    UserNotFoundByIdError,
)
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeUserEmailCommand:
    user_id: UUID
    email: str


class ChangeUserEmailCommandHandler:
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

    async def __call__(self, data: ChangeUserEmailCommand) -> None:

        validated_email = UserEmail(data.email)
        existing: User | None = await self._user_gateway.read_by_email(validated_email)
        if existing is None:
            msg = f"Could not find user with email '{data.email}'"
            raise UserNotFoundByEmailError(msg)
        if existing is not None and existing.email != validated_email:
            msg = "User with this email already exists"
            raise EmailAlreadyExistsError(msg)

        current_user: User = await self._current_user_service.get_current_user()

        user_for_update_email: User | None = await self._user_gateway.read_by_id(UserID(data.user_id))

        if user_for_update_email is None:
            msg = f"Can't find user with id {data.user_id}"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(user_for_update_email, current_user):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        self._user_service.change_email(user=user_for_update_email, email=validated_email)
        await self._transaction_manager.commit()
