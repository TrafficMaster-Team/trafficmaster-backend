from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from trafficmaster.application.queries.deck.read_public_decks import ReadPublicDecksQuery, ReadPublicDecksQueryHandler
from trafficmaster.presentation.http.v1.common.cache_control import enable_public_cache
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.routes.deck.read_public.schemas import (
    PublicDeckResponseSchema,
    ReadPublicDecksRequestSchema,
    ReadPublicDecksResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck.public_deck import PublicDeckView

read_public_decks_route: Final[APIRouter] = APIRouter(tags=["Deck"], route_class=DishkaRoute)


@read_public_decks_route.get(
    "/public",
    status_code=status.HTTP_200_OK,
    summary="Get public decks",
    description=getdoc(ReadPublicDecksQueryHandler),
    response_model=ReadPublicDecksResponseSchema,
    dependencies=[Depends(enable_public_cache)],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_public_decks(
    request: Annotated[ReadPublicDecksRequestSchema, Depends()],
    interactor: FromDishka[ReadPublicDecksQueryHandler],
) -> ReadPublicDecksResponseSchema:
    query: ReadPublicDecksQuery = ReadPublicDecksQuery(limit=request.limit, offset=request.offset)

    views: list[PublicDeckView] = await interactor(data=query)

    return ReadPublicDecksResponseSchema(decks=[PublicDeckResponseSchema(**asdict(view)) for view in views])
