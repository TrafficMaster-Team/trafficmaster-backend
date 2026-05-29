from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

import pydantic
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from trafficmaster.domain.common.errors import DomainFieldError


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaRich:
    description: str
    details: list[dict[str, Any]] | None = None


class ExceptionHandler:
    _ERROR_MAPPING: Final[MappingProxyType[type[Exception], int]] = MappingProxyType(
        {
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
        }
    )

    def __init__(self, app: FastAPI) -> None:
        self._app: Final[FastAPI] = app
        self._internal_server_error: Final[int] = 500

    async def _handle(self, _: Request, exc: Exception) -> JSONResponse:
        status_code: int = self._ERROR_MAPPING.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

        response: ExceptionSchema | ExceptionSchemaRich
        if isinstance(exc, pydantic.ValidationError):
            response = ExceptionSchemaRich(str(exc), jsonable_encoder(exc.errors))
        elif status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            message_if_unavailable: str = "Service temporary unavailable. Please try later."
            response = ExceptionSchema(message_if_unavailable)
        else:
            message: str = str(exc) if status_code < self._internal_server_error else "Internal server error"
            response = ExceptionSchema(message)

        return JSONResponse(response=response, status_code=status_code)

    def setup_handlers(self) -> None:
        for exc_class in self._ERROR_MAPPING:
            self._app.add_exception_handler(exc_class, self._handle)
        self._app.add_exception_handler(Exception, self._handle)
