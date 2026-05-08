from abc import abstractmethod
from typing import Protocol

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.domain.user.values.user_id import UserID


class AuthSessionGateway(Protocol):
    @abstractmethod
    async def add(self, auth_session: AuthSession) -> None: ...

    @abstractmethod
    async def update(self, auth_session: AuthSession) -> None: ...

    @abstractmethod
    async def read_by_id(self, auth_session_id: str) -> AuthSession | None: ...

    @abstractmethod
    async def delete(self, auth_session_id: str) -> None: ...

    @abstractmethod
    async def delete_all_for_user(self, user_id: UserID) -> None: ...
