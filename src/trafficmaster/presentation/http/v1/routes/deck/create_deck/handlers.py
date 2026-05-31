from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, status

from trafficmaster.application.commands.deck.create_deck import CreateDeckCommand, CreateDeckCommandHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.deck.create_deck.schemas import (
    CreateDeckRequestSchema,
    CreateDeckResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.deck.create_deck import CreateDeckView

create_deck_route: Final[APIRouter] = APIRouter(tags=["Deck"], route_class=DishkaRoute)


@create_deck_route.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a deck",
    description=getdoc(CreateDeckCommandHandler),
    response_model=CreateDeckResponseSchema,
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
async def create_deck(
    request: CreateDeckRequestSchema,
    interactor: FromDishka[CreateDeckCommandHandler],
) -> CreateDeckResponseSchema:
    command: CreateDeckCommand = CreateDeckCommand(
        owner_id=request.owner_id,
        deck_config_id=request.deck_config_id,
        title=request.title,
        description=request.description,
        is_public=request.is_public,
    )

    view: CreateDeckView = await interactor(data=command)

    return CreateDeckResponseSchema(id=view.id)
