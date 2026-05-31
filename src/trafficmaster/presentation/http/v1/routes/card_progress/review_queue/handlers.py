from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from fastapi.params import Security

from trafficmaster.application.queries.card_progress.read_review_queue import (
    ReadReviewQueueQuery,
    ReadReviewQueueQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card_progress.review_queue.schemas import (
    ReviewQueueItemSchema,
    ReviewQueueResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card_progress.review_queue_item import ReviewQueueItemView

review_queue_route: Final[APIRouter] = APIRouter(tags=["Card Progress"], route_class=DishkaRoute)


@review_queue_route.get(
    "/queue",
    status_code=status.HTTP_200_OK,
    summary="Get the review queue for a deck",
    description=getdoc(ReadReviewQueueQueryHandler),
    response_model=ReviewQueueResponseSchema,
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
async def read_review_queue(
    interactor: FromDishka[ReadReviewQueueQueryHandler],
    deck_id: Annotated[UUID, Query(description="The ID of the deck whose review queue to read")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum number of cards to return")] = 50,
) -> ReviewQueueResponseSchema:
    query: ReadReviewQueueQuery = ReadReviewQueueQuery(deck_id=deck_id, limit=limit)

    views: list[ReviewQueueItemView] = await interactor(data=query)

    return ReviewQueueResponseSchema(items=[ReviewQueueItemSchema.model_validate(view) for view in views])
