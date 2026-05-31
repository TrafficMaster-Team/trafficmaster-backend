from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.deck.copy_deck import CopyDeckCommand, CopyDeckCommandHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck.copy_deck.schemas import CopyDeckResponseSchema

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck.copy_deck import CopyDeckView

copy_deck_route: Final[APIRouter] = APIRouter(tags=["Deck"], route_class=DishkaRoute)


DeckIDPathParameter = Path(
    title="The ID of the deck to copy",
    description="The ID of the source deck to copy. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@copy_deck_route.post(
    "/{deck_id}/copy",
    status_code=status.HTTP_201_CREATED,
    summary="Copy a deck",
    description=getdoc(CopyDeckCommandHandler),
    response_model=CopyDeckResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def copy_deck(
    deck_id: Annotated[UUID, DeckIDPathParameter],
    interactor: FromDishka[CopyDeckCommandHandler],
) -> CopyDeckResponseSchema:
    command: CopyDeckCommand = CopyDeckCommand(source_deck_id=deck_id)

    view: CopyDeckView = await interactor(data=command)

    return CopyDeckResponseSchema(**asdict(view))
