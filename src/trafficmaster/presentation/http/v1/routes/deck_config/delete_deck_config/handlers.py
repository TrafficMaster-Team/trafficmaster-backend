from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.deck_config.delete_deck_config import (
    DeleteDeckConfigCommand,
    DeleteDeckConfigCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme

delete_deck_config_route: Final[APIRouter] = APIRouter(tags=["Deck Config"], route_class=DishkaRoute)


DeckConfigIDPathParameter = Path(
    title="The ID of the deck config",
    description="The ID of the deck config. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@delete_deck_config_route.delete(
    "/{deck_config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a deck config",
    description=getdoc(DeleteDeckConfigCommandHandler),
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def delete_deck_config(
    deck_config_id: Annotated[UUID, DeckConfigIDPathParameter],
    interactor: FromDishka[DeleteDeckConfigCommandHandler],
) -> None:
    command: DeleteDeckConfigCommand = DeleteDeckConfigCommand(deck_config_id=deck_config_id)

    await interactor(data=command)
