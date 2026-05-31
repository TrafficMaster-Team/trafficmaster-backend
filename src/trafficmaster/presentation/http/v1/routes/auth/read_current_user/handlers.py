from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status
from fastapi.params import Security

from trafficmaster.application.auth.read_current_user import ReadCurrentUserHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.user.read.schemas import ReadUserByIDResponse

if TYPE_CHECKING:
    from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView

read_current_user_route: Final[APIRouter] = APIRouter(tags=["Auth"], route_class=DishkaRoute)


@read_current_user_route.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get the current authenticated user",
    description=getdoc(ReadCurrentUserHandler),
    response_model=ReadUserByIDResponse,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def read_current_user(
    interactor: FromDishka[ReadCurrentUserHandler],
) -> ReadUserByIDResponse:
    view: ReadUserByIDView = await interactor()

    return ReadUserByIDResponse(**asdict(view))
