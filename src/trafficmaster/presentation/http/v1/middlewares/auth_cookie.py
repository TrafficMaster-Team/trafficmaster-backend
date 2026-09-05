from http.cookies import SimpleCookie
from typing import Final

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from trafficmaster.presentation.http.v1.common.auth_cookie import (
    ACCESS_TOKEN_COOKIE_KEY,
    REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY,
    REQUEST_STATE_NEW_ACCESS_TOKEN_KEY,
    AuthCookieParams,
)


class AuthCookieMiddleware:
    def __init__(self, app: ASGIApp, cookie_params: AuthCookieParams) -> None:
        self._app: Final[ASGIApp] = app
        self._cookie_params: Final[AuthCookieParams] = cookie_params

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self._app(scope, receive, send)

        request = Request(scope)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                if self._delete_cookie_requested(request):
                    self._delete_cookie(headers)
                else:
                    self._maybe_set_cookie(request, headers)

            await send(message)

        return await self._app(scope, receive, send_wrapper)

    def _delete_cookie_requested(self, request: Request) -> bool:
        return bool(getattr(request.state, REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY, False))

    def _maybe_set_cookie(self, request: Request, headers: MutableHeaders) -> None:
        new_access_token: str | None = getattr(request.state, REQUEST_STATE_NEW_ACCESS_TOKEN_KEY, None)
        if new_access_token is None:
            return

        cookie_header = self._make_cookie_header(value=new_access_token)
        headers.append("Set-Cookie", cookie_header)

    def _delete_cookie(self, headers: MutableHeaders) -> None:
        cookie_header = self._make_cookie_header(value="", max_age=0)
        headers.append("Set-Cookie", cookie_header)

    def _make_cookie_header(self, *, value: str, max_age: int | None = None) -> str:
        cookie = SimpleCookie()
        cookie[ACCESS_TOKEN_COOKIE_KEY] = value
        cookie[ACCESS_TOKEN_COOKIE_KEY]["path"] = "/"
        cookie[ACCESS_TOKEN_COOKIE_KEY]["httponly"] = True
        cookie[ACCESS_TOKEN_COOKIE_KEY]["samesite"] = self._cookie_params.same_site

        if self._cookie_params.secure:
            cookie[ACCESS_TOKEN_COOKIE_KEY]["secure"] = True
        if max_age is not None:
            cookie[ACCESS_TOKEN_COOKIE_KEY]["max-age"] = max_age

        return cookie.output(header="").strip()
