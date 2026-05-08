from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.auth.sign_up import SignUpView
from trafficmaster.application.errors.auth import AlreadyAuthenticatedError, AuthenticationError
from trafficmaster.application.errors.gateway import GatewayError
from trafficmaster.application.errors.user import UserAlreadyExistsError
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.raw_password import RawPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(slots=True, kw_only=True, frozen=True)
class SignUpData:
    email: str
    name: str
    password: str
    role: UserRole = UserRole.USER


class SignUpHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_gateway: UserGateway,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_service: Final[UserService] = user_service
        self._user_gateway: Final[UserGateway] = user_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager

    async def __call__(self, data: SignUpData) -> SignUpView:

        try:
            await self._current_user_service.get_current_user()
            msg = "Already authenticated"
            raise AlreadyAuthenticatedError(msg)
        except AuthenticationError:
            pass

        new_user: User = self._user_service.create_user(
            email=UserEmail(data.email),
            name=Username(data.name),
            raw_password=RawPassword(data.password),
            role=UserRole(data.role),
        )

        if (await self._user_gateway.read_by_email(new_user.email)) is not None:
            msg = "User with this email already exists"
            raise UserAlreadyExistsError(msg)

        try:
            await self._user_gateway.add(new_user)
            await self._transaction_manager.commit()

        except GatewayError as error:
            msg = "Authentication failed"
            raise AuthenticationError(msg) from error

        return SignUpView(id=new_user.id)
