from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, status
from fastapi.params import Security

from trafficmaster.application.queries.card.read_by_id import ReadCardByIdQuery, ReadCardByIdQueryHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card.read.schemas import ReadCardResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card.read_by_id import ReadCardByIDView

read_card_route: Final[APIRouter] = APIRouter(tags=["Card"], route_class=DishkaRoute)


CardIDPathParameter = Path(
    title="The ID of the card",
    description="The ID of the card. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@read_card_route.get(
    "/{card_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a card by ID",
    description=getdoc(ReadCardByIdQueryHandler),
    response_model=ReadCardResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_card_by_id(
    card_id: Annotated[UUID, CardIDPathParameter],
    interactor: FromDishka[ReadCardByIdQueryHandler],
) -> ReadCardResponseSchema:
    query: ReadCardByIdQuery = ReadCardByIdQuery(card_id=card_id)

    view: ReadCardByIDView = await interactor(data=query)

    return ReadCardResponseSchema(**asdict(view))
