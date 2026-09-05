from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from trafficmaster.presentation.http.v1.common.cache_control import DEFAULT_CACHE_CONTROL


class ClientCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response: Response = await call_next(request)
        response.headers.setdefault("Cache-Control", DEFAULT_CACHE_CONTROL)
        return response
