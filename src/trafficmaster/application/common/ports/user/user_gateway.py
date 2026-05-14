from typing import Protocol

from trafficmaster.application.common.query_params.user_filters import UserParams
from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID


class UserGateway(Protocol):
    async def add(self, user: User) -> None: ...

    async def delete_by_id(self, user_id: UserID) -> None: ...

    async def read_by_id(self, user_id: UserID) -> User | None: ...

    async def read_by_email(self, user_email: UserEmail) -> User | None: ...

    async def read_all_users(self, user_params: UserParams) -> list[User]: ...
