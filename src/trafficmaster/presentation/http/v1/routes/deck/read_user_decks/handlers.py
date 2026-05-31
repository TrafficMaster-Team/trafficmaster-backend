from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from fastapi.params import Security

from trafficmaster.application.queries.deck.read_decks_by_user_id import (
    ReadDecksByUserIdQuery,
    ReadDecksByUserIdQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck.read.schemas import ReadDeckResponseSchema
from trafficmaster.presentation.http.v1.routes.deck.read_user_decks.schemas import ReadUserDecksResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck.read_by_id import ReadDeckByIDView

read_user_decks_route: Final[APIRouter] = APIRouter(tags=["Deck"], route_class=DishkaRoute)


UserIDQueryParameter = Query(
    title="The ID of the user whose decks to read",
    description="The ID of the user whose decks to read. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@read_user_decks_route.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get decks owned by a user",
    description=getdoc(ReadDecksByUserIdQueryHandler),
    response_model=ReadUserDecksResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_user_decks(
    user_id: Annotated[UUID, UserIDQueryParameter],
    interactor: FromDishka[ReadDecksByUserIdQueryHandler],
) -> ReadUserDecksResponseSchema:
    query: ReadDecksByUserIdQuery = ReadDecksByUserIdQuery(user_id=user_id)

    views: list[ReadDeckByIDView] = await interactor(data=query)

    return ReadUserDecksResponseSchema(decks=[ReadDeckResponseSchema(**asdict(view)) for view in views])
