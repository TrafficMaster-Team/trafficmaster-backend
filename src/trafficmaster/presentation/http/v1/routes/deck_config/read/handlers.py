from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, status
from fastapi.params import Security

from trafficmaster.application.queries.deck_config.read_by_id import (
    ReadDeckConfigByIdQuery,
    ReadDeckConfigByIdQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck_config.read.schemas import ReadDeckConfigResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck_config.read_by_id import ReadDeckConfigByIDView

read_deck_config_route: Final[APIRouter] = APIRouter(tags=["Deck Config"], route_class=DishkaRoute)


DeckConfigIDPathParameter = Path(
    title="The ID of the deck config",
    description="The ID of the deck config. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@read_deck_config_route.get(
    "/{deck_config_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a deck config by ID",
    description=getdoc(ReadDeckConfigByIdQueryHandler),
    response_model=ReadDeckConfigResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_deck_config_by_id(
    deck_config_id: Annotated[UUID, DeckConfigIDPathParameter],
    interactor: FromDishka[ReadDeckConfigByIdQueryHandler],
) -> ReadDeckConfigResponseSchema:
    query: ReadDeckConfigByIdQuery = ReadDeckConfigByIdQuery(deck_config_id=deck_config_id)

    view: ReadDeckConfigByIDView = await interactor(data=query)

    return ReadDeckConfigResponseSchema.model_validate(view)
