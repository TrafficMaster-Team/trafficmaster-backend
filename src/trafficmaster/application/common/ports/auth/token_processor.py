from typing import Protocol

from trafficmaster.application.auth.auth_model import AuthSession


class AuthSessionTokenProcessor(Protocol):
    def encode(self, auth_session: AuthSession) -> str: ...

    def decode_auth_session_id(self, access_token: str) -> str | None: ...
