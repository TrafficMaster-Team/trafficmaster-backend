from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.deck.assign_deck_config import (
    AssignDeckConfigCommand,
    AssignDeckConfigCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck.assign_config.schemas import AssignDeckConfigRequestSchema

assign_config_route: Final[APIRouter] = APIRouter(tags=["Deck"], route_class=DishkaRoute)


DeckIDPathParameter = Path(
    title="The ID of the deck",
    description="The ID of the deck. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@assign_config_route.patch(
    "/{deck_id}/config",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a deck config to a deck",
    description=getdoc(AssignDeckConfigCommandHandler),
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
async def assign_deck_config(
    deck_id: Annotated[UUID, DeckIDPathParameter],
    request: AssignDeckConfigRequestSchema,
    interactor: FromDishka[AssignDeckConfigCommandHandler],
) -> None:
    command: AssignDeckConfigCommand = AssignDeckConfigCommand(
        deck_id=deck_id,
        deck_config_id=request.deck_config_id,
    )

    await interactor(data=command)
