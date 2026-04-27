from abc import abstractmethod
from typing import Protocol

from trafficmaster.domain.user.values.user_id import UserID


class UserIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> UserID:
        raise NotImplementedError
