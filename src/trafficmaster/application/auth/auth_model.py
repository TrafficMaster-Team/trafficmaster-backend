from dataclasses import dataclass
from datetime import datetime

from trafficmaster.domain.user.values.user_id import UserID


@dataclass(slots=True, eq=True, kw_only=True)
class AuthSession:
    id_: str
    user_id: UserID
    expiration: datetime
