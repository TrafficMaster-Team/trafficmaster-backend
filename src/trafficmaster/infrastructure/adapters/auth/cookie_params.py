from dataclasses import dataclass
from typing import Literal


@dataclass(eq=False, slots=True, kw_only=True)
class CookieParams:
    secure: bool
    same_site: Literal["strict"] | None = None

    def __post_init__(self) -> None:
        if self.secure and self.same_site is None:
            self.same_site = "strict"
