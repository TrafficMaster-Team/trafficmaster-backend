import re
from dataclasses import dataclass
from typing import Final, override

from trafficmaster.domain.common.values.base_value import BaseValueObject
from trafficmaster.domain.user.errors.user import (
    BadUsernameError,
    TooBigUsernameError,
    TooSmallUsernameError,
    UsernameCantBeEmptyError,
)

MAX_LENGTH_USERNAME: Final[int] = 255
MIN_LENGTH_USERNAME: Final[int] = 2

# starts with a letter or a number
PATTERN_START: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z0-9]",
)

# ends with a letter or a number
PATTERN_END: Final[re.Pattern[str]] = re.compile(
    r".*[a-zA-Z0-9]$",
)

PATTERN_ALLOWED_CHARS: Final[re.Pattern[str]] = re.compile(
    r"[a-zA-Z0-9._-]*",
)

PATTERN_NO_CONCUSSIVE_CHARS: Final[re.Pattern[str]] = re.compile("[-_.]{2,}")


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class Username(BaseValueObject):
    name: str

    @override
    def _validate(self) -> None:

        if len(self.name) > MAX_LENGTH_USERNAME:
            msg = f"User name must be at most {MAX_LENGTH_USERNAME} characters"
            raise TooBigUsernameError(msg)

        if len(self.name) < MIN_LENGTH_USERNAME:
            msg = f"User name must be at least {MIN_LENGTH_USERNAME} characters"
            raise TooSmallUsernameError(msg)

        if self.name.isspace() or self.name == "":
            msg = f"User name cannot be empty: {self.name}"
            raise UsernameCantBeEmptyError(msg)

        if not re.match(PATTERN_START, self.name):
            msg = "Name must start with a letter or number."
            raise BadUsernameError(msg)

        if not re.fullmatch(PATTERN_ALLOWED_CHARS, self.name):
            msg = (
                f"Invalid characters in name: {self.name}"
                f"Name must contain only letters, digits,"
                f"dots, hyphens, and underscores."
            )
            raise BadUsernameError(msg)

        if re.search(PATTERN_NO_CONCUSSIVE_CHARS, self.name):
            msg = "Name mustn't contain double concussive (dot, hyphen, underscore) characters."
            raise BadUsernameError(msg)

        if not re.fullmatch(PATTERN_END, self.name):
            msg = "Name must end with a letter or a number."
            raise BadUsernameError(msg)

    @override
    def __str__(self) -> str:
        return self.name
