from dataclasses import dataclass

from trafficmaster.domain.common.errors import DomainFieldError
from trafficmaster.domain.common.values.base_value import BaseValueObject


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class IntValue(BaseValueObject):
    value: int

    def _validate(self) -> None: ...

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class PositiveValue(BaseValueObject):
    value: int

    def _validate(self) -> None:
        if self.value < 0:
            msg = "value must be non-negative"
            raise DomainFieldError(msg)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class EmptyValue(BaseValueObject):
    def _validate(self) -> None: ...

    def __str__(self) -> str:
        return ""


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class SuperValidateValue(BaseValueObject):
    value: int

    def _validate(self) -> None:
        super()._validate()

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class SuperStrValue(BaseValueObject):
    value: int

    def _validate(self) -> None: ...

    def __str__(self) -> str:
        return super().__str__()
