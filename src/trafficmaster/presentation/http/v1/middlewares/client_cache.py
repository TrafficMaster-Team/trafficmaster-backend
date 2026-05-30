from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class ClientCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_age: int = 60) -> None:
        super().__init__(app)
        self.max_age = max_age

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response: Response = await call_next(request)
        response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
        return response
