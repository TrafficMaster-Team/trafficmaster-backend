from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, Query, status
from fastapi.params import Security

from trafficmaster.application.queries.card_progress.read_review_log_by_card import (
    ReadReviewLogByCardQuery,
    ReadReviewLogByCardQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card_progress.review_log_by_card.schemas import (
    ReviewLogResponseSchema,
    ReviewLogsResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card_progress.review_log import ReviewLogView

review_log_by_card_route: Final[APIRouter] = APIRouter(tags=["Card Progress"], route_class=DishkaRoute)


CardIDPathParameter = Path(
    title="The ID of the card",
    description="The ID of the card whose review logs to read. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f"],
)


@review_log_by_card_route.get(
    "/card/{card_id}/logs",
    status_code=status.HTTP_200_OK,
    summary="Get review logs for a card",
    description=getdoc(ReadReviewLogByCardQueryHandler),
    response_model=ReviewLogsResponseSchema,
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
async def read_review_log_by_card(
    card_id: Annotated[UUID, CardIDPathParameter],
    interactor: FromDishka[ReadReviewLogByCardQueryHandler],
    limit: Annotated[int | None, Query(ge=1, le=100, description="Limit for pagination")] = None,
    offset: Annotated[int | None, Query(ge=0, description="Offset for pagination")] = None,
) -> ReviewLogsResponseSchema:
    query: ReadReviewLogByCardQuery = ReadReviewLogByCardQuery(card_id=card_id, limit=limit, offset=offset)

    views: list[ReviewLogView] = await interactor(data=query)

    return ReviewLogsResponseSchema(logs=[ReviewLogResponseSchema.model_validate(view) for view in views])
