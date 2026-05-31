from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, status
from fastapi.params import Security

from trafficmaster.application.queries.card_progress.preview_review_intervals import (
    PreviewReviewIntervalsQuery,
    PreviewReviewIntervalsQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card_progress.preview_intervals.schemas import (
    PreviewReviewIntervalsResponseSchema,
    ReviewPreviewItemSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card_progress.preview_review_intervals import (
        PreviewReviewIntervalsView,
    )

preview_intervals_route: Final[APIRouter] = APIRouter(tags=["Card Progress"], route_class=DishkaRoute)


CardIDPathParameter = Path(
    title="The ID of the card",
    description="The ID of the card to preview intervals for. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@preview_intervals_route.get(
    "/card/{card_id}/preview",
    status_code=status.HTTP_200_OK,
    summary="Preview review intervals for a card",
    description=getdoc(PreviewReviewIntervalsQueryHandler),
    response_model=PreviewReviewIntervalsResponseSchema,
    dependencies=[Security(cookie_scheme)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def preview_review_intervals(
    card_id: Annotated[UUID, CardIDPathParameter],
    interactor: FromDishka[PreviewReviewIntervalsQueryHandler],
) -> PreviewReviewIntervalsResponseSchema:
    query: PreviewReviewIntervalsQuery = PreviewReviewIntervalsQuery(card_id=card_id)

    view: PreviewReviewIntervalsView = await interactor(data=query)

    return PreviewReviewIntervalsResponseSchema(
        items=[ReviewPreviewItemSchema.model_validate(item) for item in view.items],
    )
