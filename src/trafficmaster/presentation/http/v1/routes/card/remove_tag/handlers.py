from inspect import getdoc
from typing import Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.card.remove_tag import RemoveTagCommand, RemoveTagCommandHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme

remove_tag_route: Final[APIRouter] = APIRouter(tags=["Card"], route_class=DishkaRoute)


CardIDPathParameter = Path(
    title="The ID of the card",
    description="The ID of the card. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)
TagPathParameter = Path(
    title="The tag to remove",
    description="The tag value to remove from the card",
    examples=["grammar"],
)


@remove_tag_route.delete(
    "/{card_id}/tags/{tag}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a tag from a card",
    description=getdoc(RemoveTagCommandHandler),
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
async def remove_tag(
    card_id: Annotated[UUID, CardIDPathParameter],
    tag: Annotated[str, TagPathParameter],
    interactor: FromDishka[RemoveTagCommandHandler],
) -> None:
    command: RemoveTagCommand = RemoveTagCommand(card_id=card_id, tag=tag)

    await interactor(data=command)
