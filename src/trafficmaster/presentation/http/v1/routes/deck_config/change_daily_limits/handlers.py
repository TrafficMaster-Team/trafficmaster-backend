from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.deck_config.change_daily_limits import (
    ChangeDailyLimitsCommand,
    ChangeDailyLimitsCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck_config.shared_schemas import DailyLimitsSchema

change_daily_limits_route: Final[APIRouter] = APIRouter(tags=["Deck Config"], route_class=DishkaRoute)


DeckConfigIDPathParameter = Path(
    title="The ID of the deck config",
    description="The ID of the deck config. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@change_daily_limits_route.patch(
    "/{deck_config_id}/daily-limits",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change deck config daily limits",
    description=getdoc(ChangeDailyLimitsCommandHandler),
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
async def change_daily_limits(
    deck_config_id: Annotated[UUID, DeckConfigIDPathParameter],
    request: DailyLimitsSchema,
    interactor: FromDishka[ChangeDailyLimitsCommandHandler],
) -> None:
    command: ChangeDailyLimitsCommand = ChangeDailyLimitsCommand(
        deck_config_id=deck_config_id,
        daily_limits=request.to_domain(),
    )

    await interactor(data=command)
