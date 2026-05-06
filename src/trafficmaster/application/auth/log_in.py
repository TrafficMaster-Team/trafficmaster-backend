from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.auth_session import AuthSessionService
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.auth import AlreadyAuthenticatedError, AuthenticationError
from trafficmaster.application.errors.user import UserNotFoundByEmailError
from trafficmaster.domain.user.services.user_service import UserService
from trafficmaster.domain.user.values.raw_password import RawPassword
from trafficmaster.domain.user.values.user_email import UserEmail

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, kw_only=True, slots=True)
class LogInData:
    email: str
    password: str


class LogInHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_gateway: UserGateway,
        user_service: UserService,
        auth_service: AuthSessionService,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_gateway: Final[UserGateway] = user_gateway
        self._user_service: Final[UserService] = user_service
        self._auth_service: Final[AuthSessionService] = auth_service

    async def __call__(self, data: LogInData) -> None:

        try:
            await self._current_user_service.get_current_user()
            msg = "You are already logged in"
            raise AlreadyAuthenticatedError(msg)
        except AuthenticationError:
            pass

        email: UserEmail = UserEmail(data.email)
        raw_password: RawPassword = RawPassword(data.password)
        user: User | None = await self._user_gateway.read_by_email(email)
        if user is None:
            msg = f"User with email {email.email} does not exist"
            raise UserNotFoundByEmailError(msg)

        if not self._user_service.verify_password(user, raw_password):
            msg = f"User with email {email.email} has incorrect password"
            raise AuthenticationError(msg)

        if not user.is_active:
            msg = f"User with email {email.email} has inactive account"
            raise AuthenticationError(msg)

        await self._auth_service.create_session(user.id)
