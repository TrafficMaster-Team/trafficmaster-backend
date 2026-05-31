from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.card.change_image_path import (
    ChangeImagePathCommand,
    ChangeImagePathCommandHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card.change_image.schemas import ChangeImagePathRequestSchema

change_image_route: Final[APIRouter] = APIRouter(tags=["Card"], route_class=DishkaRoute)


CardIDPathParameter = Path(
    title="The ID of the card",
    description="The ID of the card. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@change_image_route.patch(
    "/{card_id}/image",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change card image path",
    description=getdoc(ChangeImagePathCommandHandler),
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
async def change_card_image(
    card_id: Annotated[UUID, CardIDPathParameter],
    request: ChangeImagePathRequestSchema,
    interactor: FromDishka[ChangeImagePathCommandHandler],
) -> None:
    command: ChangeImagePathCommand = ChangeImagePathCommand(card_id=card_id, image_path=request.image_path)

    await interactor(data=command)
