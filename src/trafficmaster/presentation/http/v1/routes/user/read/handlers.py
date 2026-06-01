from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

if TYPE_CHECKING:
    from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView
from trafficmaster.application.queries.user.read_by_id import ReadUserByIdQuery, ReadUserByIdQueryHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.user.read.schemas import ReadUserByIDResponse

read_router: Final[APIRouter] = APIRouter(tags=["User"], route_class=DishkaRoute)

UserIDPathParameter = Path(
    title="The ID of the user to get",
    description="The ID of the user to get. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f", "75079971-fb0e-4e04-bf07-ceb57faebe84"],
)


@read_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Security(cookie_scheme)],
    description=getdoc(ReadUserByIdQueryHandler),
    response_model=ReadUserByIDResponse,
    summary="Get user by ID",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def read_user_by_id_handler(
    user_id: Annotated[UUID, UserIDPathParameter],
    interactor: FromDishka[ReadUserByIdQueryHandler],
) -> ReadUserByIDResponse:
    query: ReadUserByIdQuery = ReadUserByIdQuery(user_id=user_id)

    view: ReadUserByIDView = await interactor(data=query)

    return ReadUserByIDResponse(id=view.id, name=view.name, email=view.email, role=view.role)
