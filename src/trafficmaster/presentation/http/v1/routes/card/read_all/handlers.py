from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status
from fastapi.params import Depends, Security

from trafficmaster.application.queries.card.read_all_cards import ReadAllCardsQuery, ReadAllCardsQueryHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card.read.schemas import ReadCardResponseSchema
from trafficmaster.presentation.http.v1.routes.card.read_all.schemas import (
    ReadAllCardsRequestSchema,
    ReadAllCardsResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card.read_by_id import ReadCardByIDView

read_all_cards_route: Final[APIRouter] = APIRouter(tags=["Card"], route_class=DishkaRoute)


@read_all_cards_route.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all cards of a deck",
    description=getdoc(ReadAllCardsQueryHandler),
    response_model=ReadAllCardsResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_all_cards(
    request: Annotated[ReadAllCardsRequestSchema, Depends()],
    interactor: FromDishka[ReadAllCardsQueryHandler],
) -> ReadAllCardsResponseSchema:
    query: ReadAllCardsQuery = ReadAllCardsQuery(
        deck_id=request.deck_id,
        limit=request.limit,
        offset=request.offset,
        sorting_field=request.sorting_field,
        sorting_order=request.sorting_order,
        tags=request.tags,
    )

    views: list[ReadCardByIDView] = await interactor(data=query)

    return ReadAllCardsResponseSchema(cards=[ReadCardResponseSchema(**asdict(view)) for view in views])
