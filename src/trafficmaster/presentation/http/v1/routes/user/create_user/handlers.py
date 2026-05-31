from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, status

from trafficmaster.application.commands.user.create_user import CreateUserCommand, CreateUserCommandHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.user.create_user.schemas import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.user.create_user import CreateUserView

create_user_route: Final[APIRouter] = APIRouter(
    route_class=DishkaRoute,
    tags=["User"],
)


@create_user_route.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description=getdoc(CreateUserCommandHandler),
    dependencies=[Security(cookie_scheme)],
    response_model=CreateUserResponseSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def create_user(
    request: CreateUserRequestSchema,
    interactor: FromDishka[CreateUserCommandHandler],
) -> CreateUserResponseSchema:
    command: CreateUserCommand = CreateUserCommand(
        email=request.email,
        username=request.username,
        password=request.password,
        role=request.role,
    )

    view: CreateUserView = await interactor(data=command)

    return CreateUserResponseSchema(id=view.id)
