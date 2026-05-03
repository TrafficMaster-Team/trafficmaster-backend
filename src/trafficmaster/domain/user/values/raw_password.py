from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.user.errors.password import (
    EmptyPasswordWasProvidedError,
    WeakPasswordWasProvidedError,
)

MIN_LENGTH_PASSWORD: Final[int] = 8
MAX_LENGTH_PASSWORD: Final[int] = 255


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class RawPassword(BaseValueObject):
    password: str

    @override
    def _validate(self) -> None:

        if self.password == "" or self.password.isspace():
            msg = "Please enter a password."
            raise EmptyPasswordWasProvidedError(msg)

        if self.password.isdigit():
            msg = "Password must contain at least one letter."
            raise WeakPasswordWasProvidedError(msg)

        if self.password.isalpha():
            msg = "Password must contain at least one digit."
            raise WeakPasswordWasProvidedError(msg)

        if len(self.password) < MIN_LENGTH_PASSWORD:
            msg = f"Password must be at least {MIN_LENGTH_PASSWORD} characters long."
            raise WeakPasswordWasProvidedError(msg)

        if len(self.password) > MAX_LENGTH_PASSWORD:
            msg = f"Password must be at most {MAX_LENGTH_PASSWORD} characters long."
            raise WeakPasswordWasProvidedError(msg)

    @override
    def __str__(self) -> str:
        return "*" * len(self.password)
