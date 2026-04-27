import re
from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.user.errors.user import WrongUserEmailFormatError

EMAIL_REGEX_COMPILED_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class UserEmail(BaseValueObject):
    email: str

    @override
    def _validate(self) -> None:
        if not re.fullmatch(EMAIL_REGEX_COMPILED_PATTERN, self.email):
            msg = f"Invalid email address: {self.email}"
            raise WrongUserEmailFormatError(msg)

        if ".." in self.email:
            msg = f"Invalid email address: {self.email}"
            raise WrongUserEmailFormatError(msg)

    @override
    def __str__(self) -> str:
        return self.email
