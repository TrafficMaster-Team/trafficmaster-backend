from typing import Final

from trafficmaster.application.common.ports.access_revoke import AccessRevoker
from trafficmaster.application.common.ports.identity_provider import IdentityProvider
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.errors.auth import AuthorizationError
from trafficmaster.domain.user.entities.user import User


class CurrentUserService:
    def __init__(
        self, identity_provider: IdentityProvider, user_gateway: UserGateway, access_revoker: AccessRevoker
    ) -> None:
        self._identity_provider: Final[IdentityProvider] = identity_provider
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_revoker: Final[AccessRevoker] = access_revoker
        self._cached_user: User | None = None

    async def get_current_user(self) -> User:
        if self._cached_user is not None:
            return self._cached_user
        user_id = await self._identity_provider.get_current_user_id()
        user = await self._user_gateway.read_by_id(user_id)
        if user is None:
            msg = "User not found"
            self._access_revoker.remove_all_user_access(user_id)
            raise AuthorizationError(msg)
        self._cached_user = user
        return user
