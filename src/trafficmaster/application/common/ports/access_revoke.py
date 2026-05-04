from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.user.values.user_id import UserID


class AccessRevoker(Protocol):
    @abstractmethod
    def remove_all_user_access(self, user: UserID) -> None: ...
