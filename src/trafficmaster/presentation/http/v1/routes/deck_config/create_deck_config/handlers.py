from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, status

from trafficmaster.application.commands.deck_config.create_deck_config import (
    CreateDeckConfigCommand,
    CreateDeckConfigCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck_config.create_deck_config.schemas import (
    CreateDeckConfigRequestSchema,
    CreateDeckConfigResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck_config.create_deck_config import CreateDeckConfigView

create_deck_config_route: Final[APIRouter] = APIRouter(tags=["Deck Config"], route_class=DishkaRoute)


@create_deck_config_route.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a deck config",
    description=getdoc(CreateDeckConfigCommandHandler),
    response_model=CreateDeckConfigResponseSchema,
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
async def create_deck_config(
    request: CreateDeckConfigRequestSchema,
    interactor: FromDishka[CreateDeckConfigCommandHandler],
) -> CreateDeckConfigResponseSchema:
    command: CreateDeckConfigCommand = CreateDeckConfigCommand(
        owner_id=request.owner_id,
        name=request.name,
        daily_limits=request.daily_limits.to_domain(),
        new_cards=request.new_cards.to_domain(),
        lapses=request.lapses.to_domain(),
        advanced=request.advanced.to_domain(),
    )

    view: CreateDeckConfigView = await interactor(data=command)

    return CreateDeckConfigResponseSchema(id=view.id)
