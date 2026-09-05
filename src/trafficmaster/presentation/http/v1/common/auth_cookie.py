from dataclasses import dataclass
from typing import Final, Literal

SameSite = Literal["strict", "lax", "none"]

ACCESS_TOKEN_COOKIE_KEY: Final[str] = "access_token"  # noqa: S105
REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY: Final[str] = "delete_access_token"  # noqa: S105
REQUEST_STATE_NEW_ACCESS_TOKEN_KEY: Final[str] = "new_access_token"  # noqa: S105


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthCookieParams:
    secure: bool
    same_site: SameSite

    def __post_init__(self) -> None:
        if self.same_site == "none" and not self.secure:
            msg = 'SameSite="none" requires a secure cookie'
            raise ValueError(msg)
