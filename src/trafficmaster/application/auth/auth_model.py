from datetime import datetime

from trafficmaster.domain.user.values.user_id import UserID


class AuthSession:
    id: str
    user_id: UserID
    expiration: datetime
