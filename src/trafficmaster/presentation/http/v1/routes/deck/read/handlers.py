from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, status
from fastapi.params import Security

from trafficmaster.application.queries.deck.read_by_id import ReadDeckByIdQuery, ReadDeckByIdQueryHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck.read.schemas import ReadDeckResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck.read_by_id import ReadDeckByIDView

read_deck_route: Final[APIRouter] = APIRouter(tags=["Deck"], route_class=DishkaRoute)


DeckIDPathParameter = Path(
    title="The ID of the deck",
    description="The ID of the deck. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@read_deck_route.get(
    "/{deck_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a deck by ID",
    description=getdoc(ReadDeckByIdQueryHandler),
    response_model=ReadDeckResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_deck_by_id(
    deck_id: Annotated[UUID, DeckIDPathParameter],
    interactor: FromDishka[ReadDeckByIdQueryHandler],
) -> ReadDeckResponseSchema:
    query: ReadDeckByIdQuery = ReadDeckByIdQuery(deck_id=deck_id)

    view: ReadDeckByIDView = await interactor(data=query)

    return ReadDeckResponseSchema(**asdict(view))
