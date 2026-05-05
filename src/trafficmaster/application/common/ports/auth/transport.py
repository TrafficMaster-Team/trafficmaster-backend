from abc import abstractmethod
from typing import Protocol

from trafficmaster.application.auth.auth_model import AuthSession


class AuthSessionTransport(Protocol):
    @abstractmethod
    def deliver(self, session: AuthSession) -> None: ...

    @abstractmethod
    def extract_id(self) -> str | None: ...

    @abstractmethod
    def remove_current(self) -> None: ...
