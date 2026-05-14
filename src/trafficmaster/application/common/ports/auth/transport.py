from typing import Protocol

from trafficmaster.application.auth.auth_model import AuthSession


class AuthSessionTransport(Protocol):
    def deliver(self, session: AuthSession) -> None: ...

    def extract_id(self) -> str | None: ...

    def remove_current(self) -> None: ...
