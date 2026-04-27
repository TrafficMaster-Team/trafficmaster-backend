from dataclasses import dataclass
from typing import override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.user.errors.password import PasswordCantBeEmptyError


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class HashedPassword(BaseValueObject):
    password: bytes

    @override
    def _validate(self) -> None:
        if self.password == b"":
            msg = "Please enter a password."
            raise PasswordCantBeEmptyError(msg)

    @override
    def __str__(self) -> str:
        return str(self.password)
