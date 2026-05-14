from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.query_params.user_filters import UserParams, UserQueryFilters
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView
from trafficmaster.application.errors.user import NoPermissionToManageUserError
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_role import UserRole

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadAllUsersQuery:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ReadAllUsersQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_gateway: UserGateway,
        access_service: AccessService,
    ) -> None:
        self._access_service: Final[AccessService] = access_service
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_gateway: Final[UserGateway] = user_gateway

    async def __call__(self, data: ReadAllUsersQuery) -> list[ReadUserByIDView]:

        current_user: User = await self._current_user_service.get_current_user()
        if current_user.role == UserRole.USER:
            msg = "You don't have permission to list users"
            raise NoPermissionToManageUserError(msg)

        users: list[User] = await self._user_gateway.read_all_users(
            user_params=UserParams(
                pagination=Pagination(
                    limit=data.limit,
                    offset=data.offset,
                ),
                sorting_filter=UserQueryFilters(data.sorting_field),
                sorting_order=data.sorting_order,
            )
        )

        return [
            ReadUserByIDView(id=user.id, name=str(user.name), email=str(user.email), role=user.role) for user in users
        ]
