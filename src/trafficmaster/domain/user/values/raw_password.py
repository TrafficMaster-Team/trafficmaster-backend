from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.user.errors.password import (
    PasswordCantBeEmptyError,
    WeakPasswordWasProvidedError,
)

MIN_LENGTH_PASSWORD: Final[int] = 8
MAX_LENGTH_PASSWORD: Final[int] = 255


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class RawPassword(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:

        if self.value == "" or self.value.isspace():
            msg = "Please enter a password."
            raise PasswordCantBeEmptyError(msg)

        if self.value.isdigit():
            msg = "Password must contain at least one letter."
            raise WeakPasswordWasProvidedError(msg)

        if self.value.isalpha():
            msg = "Password must contain at least one digit."
            raise WeakPasswordWasProvidedError(msg)

        if len(self.value) < MIN_LENGTH_PASSWORD:
            msg = f"Password must be at least {MIN_LENGTH_PASSWORD} characters long."
            raise WeakPasswordWasProvidedError(msg)

        if len(self.value) > MAX_LENGTH_PASSWORD:
            msg = f"Password must be at most {MAX_LENGTH_PASSWORD} characters long."
            raise WeakPasswordWasProvidedError(msg)

    @override
    def __str__(self) -> str:
        return "*" * len(self.value)
