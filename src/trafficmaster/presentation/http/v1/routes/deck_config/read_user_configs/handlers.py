from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from fastapi.params import Security

from trafficmaster.application.queries.deck_config.read_by_user_id import (
    ReadDeckConfigsByUserIdQuery,
    ReadDeckConfigsByUserIdQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck_config.read.schemas import ReadDeckConfigResponseSchema
from trafficmaster.presentation.http.v1.routes.deck_config.read_user_configs.schemas import (
    ReadUserDeckConfigsResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck_config.read_by_id import ReadDeckConfigByIDView

read_user_configs_route: Final[APIRouter] = APIRouter(tags=["Deck Config"], route_class=DishkaRoute)


UserIDQueryParameter = Query(
    title="The ID of the user whose deck configs to read",
    description="The ID of the user whose deck configs to read. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@read_user_configs_route.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get deck configs owned by a user",
    description=getdoc(ReadDeckConfigsByUserIdQueryHandler),
    response_model=ReadUserDeckConfigsResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_user_deck_configs(
    user_id: Annotated[UUID, UserIDQueryParameter],
    interactor: FromDishka[ReadDeckConfigsByUserIdQueryHandler],
) -> ReadUserDeckConfigsResponseSchema:
    query: ReadDeckConfigsByUserIdQuery = ReadDeckConfigsByUserIdQuery(user_id=user_id)

    views: list[ReadDeckConfigByIDView] = await interactor(data=query)

    return ReadUserDeckConfigsResponseSchema(
        configs=[ReadDeckConfigResponseSchema.model_validate(view) for view in views],
    )
