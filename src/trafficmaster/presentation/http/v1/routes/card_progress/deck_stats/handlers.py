from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, status
from fastapi.params import Security

from trafficmaster.application.queries.card_progress.read_deck_stats import (
    ReadDeckStatsQuery,
    ReadDeckStatsQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card_progress.deck_stats.schemas import ReadDeckStatsResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card_progress.read_deck_stats import ReadDeckStatsView

deck_stats_route: Final[APIRouter] = APIRouter(tags=["Card Progress"], route_class=DishkaRoute)


DeckIDPathParameter = Path(
    title="The ID of the deck",
    description="The ID of the deck whose stats to read. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@deck_stats_route.get(
    "/deck/{deck_id}/stats",
    status_code=status.HTTP_200_OK,
    summary="Get study stats for a deck",
    description=getdoc(ReadDeckStatsQueryHandler),
    response_model=ReadDeckStatsResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_deck_stats(
    deck_id: Annotated[UUID, DeckIDPathParameter],
    interactor: FromDishka[ReadDeckStatsQueryHandler],
) -> ReadDeckStatsResponseSchema:
    query: ReadDeckStatsQuery = ReadDeckStatsQuery(deck_id=deck_id)

    view: ReadDeckStatsView = await interactor(data=query)

    return ReadDeckStatsResponseSchema.model_validate(view)
