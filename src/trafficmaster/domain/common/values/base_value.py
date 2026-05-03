from abc import ABC, abstractmethod
from dataclasses import dataclass, fields

from trafficmaster.domain.common.errors import DomainFieldError


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class BaseValueObject(ABC):
    def __post_init__(self) -> None:
        if not fields(self):
            msg = f"{type(self).__name__} is missing fields"
            raise DomainFieldError(msg)
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
