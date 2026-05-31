from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.user.delete_user_by_id import (
    DeleteUserByIdCommand,
    DeleteUserByIdCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme

delete_user_route: Final[APIRouter] = APIRouter(
    route_class=DishkaRoute,
    tags=["User"],
)


UserIDPathParameter = Path(
    title="The ID of the user to get",
    description="The ID of the user to get. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f", "75079971-fb0e-4e04-bf07-ceb57faebe84"],
)


@delete_user_route.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description=getdoc(DeleteUserByIdCommandHandler),
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def delete_user_by_id(
    user_id: Annotated[UUID, UserIDPathParameter],
    interactor: FromDishka[DeleteUserByIdCommandHandler],
) -> None:
    command: DeleteUserByIdCommand = DeleteUserByIdCommand(user_id=user_id)

    await interactor(data=command)
