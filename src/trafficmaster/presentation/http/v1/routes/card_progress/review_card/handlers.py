from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Security, status

from trafficmaster.application.commands.card_progress.review_card import ReviewCardCommand, ReviewCardCommandHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card_progress.review_card.schemas import (
    ReviewCardRequestSchema,
    ReviewCardResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card_progress.review_card import ReviewCardView

review_card_route: Final[APIRouter] = APIRouter(tags=["Card Progress"], route_class=DishkaRoute)


CardIDPathParameter = Path(
    title="The ID of the card",
    description="The ID of the card to review. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@review_card_route.post(
    "/card/{card_id}",
    status_code=status.HTTP_200_OK,
    summary="Review a card",
    description=getdoc(ReviewCardCommandHandler),
    response_model=ReviewCardResponseSchema,
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
async def review_card(
    card_id: Annotated[UUID, CardIDPathParameter],
    request: ReviewCardRequestSchema,
    interactor: FromDishka[ReviewCardCommandHandler],
) -> ReviewCardResponseSchema:
    command: ReviewCardCommand = ReviewCardCommand(card_id=card_id, rating=request.rating)

    view: ReviewCardView = await interactor(data=command)

    return ReviewCardResponseSchema.model_validate(view)
