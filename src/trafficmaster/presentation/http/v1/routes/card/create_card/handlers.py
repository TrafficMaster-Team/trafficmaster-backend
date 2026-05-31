from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security, status

from trafficmaster.application.commands.card.create_card import CreateCardCommand, CreateCardCommandHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card.create_card.schemas import (
    CreateCardRequestSchema,
    CreateCardResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card.create_card import CreateCardView

create_card_route: Final[APIRouter] = APIRouter(tags=["Card"], route_class=DishkaRoute)


@create_card_route.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a card",
    description=getdoc(CreateCardCommandHandler),
    response_model=CreateCardResponseSchema,
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
async def create_card(
    request: CreateCardRequestSchema,
    interactor: FromDishka[CreateCardCommandHandler],
) -> CreateCardResponseSchema:
    command: CreateCardCommand = CreateCardCommand(
        deck_id=request.deck_id,
        question=request.question,
        answer=request.answer,
        tags=request.tags,
    )

    view: CreateCardView = await interactor(data=command)

    return CreateCardResponseSchema(id=view.id)
