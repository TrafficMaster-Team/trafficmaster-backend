from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.deck_config.change_lapses import (
    ChangeLapsesCommand,
    ChangeLapsesCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck_config.shared_schemas import LapsesConfigSchema

change_lapses_route: Final[APIRouter] = APIRouter(tags=["Deck Config"], route_class=DishkaRoute)


DeckConfigIDPathParameter = Path(
    title="The ID of the deck config",
    description="The ID of the deck config. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@change_lapses_route.patch(
    "/{deck_config_id}/lapses",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change deck config lapses settings",
    description=getdoc(ChangeLapsesCommandHandler),
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
async def change_lapses(
    deck_config_id: Annotated[UUID, DeckConfigIDPathParameter],
    request: LapsesConfigSchema,
    interactor: FromDishka[ChangeLapsesCommandHandler],
) -> None:
    command: ChangeLapsesCommand = ChangeLapsesCommand(
        deck_config_id=deck_config_id,
        lapses=request.to_domain(),
    )

    await interactor(data=command)
