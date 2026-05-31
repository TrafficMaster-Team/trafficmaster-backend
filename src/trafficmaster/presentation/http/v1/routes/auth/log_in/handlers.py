from inspect import getdoc
from typing import Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from trafficmaster.application.auth.log_in import LogInData, LogInHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.routes.auth.log_in.schemas import LogInRequestSchema

log_in_route: Final[APIRouter] = APIRouter(tags=["Auth"], route_class=DishkaRoute)


@log_in_route.post(
    "/login",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log in",
    description=getdoc(LogInHandler),
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def log_in(
    request: LogInRequestSchema,
    interactor: FromDishka[LogInHandler],
) -> None:
    data: LogInData = LogInData(
        email=request.email,
        password=request.password,
    )

    await interactor(data=data)
