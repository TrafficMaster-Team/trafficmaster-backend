from typing import Final, override

from starlette.requests import Request

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.application.common.ports.auth.token_processor import AuthSessionTokenProcessor
from trafficmaster.application.common.ports.auth.transport import AuthSessionTransport
from trafficmaster.presentation.http.v1.common.auth_cookie import (
    ACCESS_TOKEN_COOKIE_KEY,
    REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY,
    REQUEST_STATE_NEW_ACCESS_TOKEN_KEY,
)


class CookieAuthSessionTransport(AuthSessionTransport):
    def __init__(self, token_processor: AuthSessionTokenProcessor, request: Request) -> None:
        self._token_processor: Final[AuthSessionTokenProcessor] = token_processor
        self._request: Final[Request] = request

    @override
    def deliver(self, auth_session: AuthSession) -> None:
        access_token = self._token_processor.encode(auth_session)
        setattr(self._request.state, REQUEST_STATE_NEW_ACCESS_TOKEN_KEY, access_token)

    @override
    def extract_id(self) -> str | None:
        access_token = self._request.cookies.get(ACCESS_TOKEN_COOKIE_KEY)
        if access_token is None:
            return None

        return self._token_processor.decode_auth_session_id(access_token)

    @override
    def remove_current(self) -> None:
        setattr(self._request.state, REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY, True)
