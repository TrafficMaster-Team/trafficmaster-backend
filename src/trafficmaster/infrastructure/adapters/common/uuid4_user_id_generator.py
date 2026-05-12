import uuid
from typing import override

from trafficmaster.domain.user.ports.id_generator import UserIDGenerator
from trafficmaster.domain.user.values.user_id import UserID


class UUID4UserIdGenerator(UserIDGenerator):
    @override
    def __call__(self) -> UserID:
        return UserID(uuid.uuid4())
