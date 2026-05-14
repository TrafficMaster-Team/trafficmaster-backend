from typing import Final, override

from starlette.requests import Request

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.application.common.ports.auth.transport import AuthSessionTransport
from trafficmaster.infrastructure.adapters.auth.jwt_token_processor import JwtAccessTokenProcessor
from trafficmaster.infrastructure.auth.cookie_params import CookieParams


class JwtAuthSessionTransport(AuthSessionTransport):
    def __init__(
        self,
        jwt_access_token_processor: JwtAccessTokenProcessor,
        request: Request,
        cookie_params: CookieParams,
    ) -> None:
        self._jwt_access_token_processor: Final[JwtAccessTokenProcessor] = jwt_access_token_processor
        self._request: Final[Request] = request
        self._cookie_params: Final[CookieParams] = cookie_params

    @override
    def deliver(self, auth_session: AuthSession) -> None:
        access_token = self._jwt_access_token_processor.encode(auth_session)
        self._request.state.new_access_token = access_token
        self._request.state.cookie_params = self._cookie_params

    @override
    def extract_id(self) -> str | None:
        access_token = self._request.cookies.get(self._cookie_params.name)
        if access_token is None:
            return None

        return self._jwt_access_token_processor.decode_auth_session_id(access_token)

    @override
    def remove_current(self) -> None:
        self._request.state.delete_access_token = True
