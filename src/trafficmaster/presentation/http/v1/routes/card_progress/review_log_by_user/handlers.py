from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from fastapi.params import Security

from trafficmaster.application.queries.card_progress.read_review_log_by_user import (
    ReadReviewLogByUserQuery,
    ReadReviewLogByUserQueryHandler,
)
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.card_progress.review_log_by_card.schemas import (
    ReviewLogResponseSchema,
    ReviewLogsResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.card_progress.review_log import ReviewLogView

review_log_by_user_route: Final[APIRouter] = APIRouter(tags=["Card Progress"], route_class=DishkaRoute)


@review_log_by_user_route.get(
    "/logs",
    status_code=status.HTTP_200_OK,
    summary="Get review logs for the current user",
    description=getdoc(ReadReviewLogByUserQueryHandler),
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
async def read_review_log_by_user(
    interactor: FromDishka[ReadReviewLogByUserQueryHandler],
    deck_id: Annotated[UUID | None, Query(description="Optionally filter logs by deck")] = None,
    limit: Annotated[int | None, Query(ge=1, le=100, description="Limit for pagination")] = None,
    offset: Annotated[int | None, Query(ge=0, description="Offset for pagination")] = None,
) -> ReviewLogsResponseSchema:
    query: ReadReviewLogByUserQuery = ReadReviewLogByUserQuery(deck_id=deck_id, limit=limit, offset=offset)

    views: list[ReviewLogView] = await interactor(data=query)

    return ReviewLogsResponseSchema(logs=[ReviewLogResponseSchema.model_validate(view) for view in views])
