from inspect import getdoc
from typing import Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, status

from trafficmaster.application.auth.log_out import LogOutHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme

log_out_route: Final[APIRouter] = APIRouter(tags=["Auth"], route_class=DishkaRoute)


@log_out_route.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out",
    description=getdoc(LogOutHandler),
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def log_out(
    interactor: FromDishka[LogOutHandler],
) -> None:
    await interactor()
