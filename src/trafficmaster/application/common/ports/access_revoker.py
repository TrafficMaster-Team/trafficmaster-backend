from typing import Protocol

from trafficmaster.domain.user.values.user_id import UserID


class AccessRevoker(Protocol):
    async def remove_all_user_access(self, user: UserID) -> None: ...
