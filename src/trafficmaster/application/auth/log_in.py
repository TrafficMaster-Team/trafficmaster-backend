from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class LoginData:
    email: str
    password: str
