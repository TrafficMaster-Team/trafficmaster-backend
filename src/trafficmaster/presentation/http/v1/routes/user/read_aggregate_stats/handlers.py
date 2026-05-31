from dataclasses import asdict
from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status
from fastapi.params import Security

from trafficmaster.application.queries.user.read_aggregate_stats import ReadUserAggregateStatsQueryHandler
from trafficmaster.presentation.http.v1.common.exception_handler import ExceptionSchema, ExceptionSchemaRich
from trafficmaster.presentation.http.v1.common.fastapi_openapi_marker import cookie_scheme
from trafficmaster.presentation.http.v1.routes.user.read_aggregate_stats.schemas import (
    ReadUserAggregateStatsResponseSchema,
)

if TYPE_CHECKING:
    from trafficmaster.application.common.views.user.aggregate_stats import UserAggregateStatsView

read_aggregate_stats_router: Final[APIRouter] = APIRouter(tags=["User"], route_class=DishkaRoute)


@read_aggregate_stats_router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    dependencies=[Security(cookie_scheme)],
    response_model=ReadUserAggregateStatsResponseSchema,
    summary="Get current user aggregate stats",
    description=getdoc(ReadUserAggregateStatsQueryHandler),
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ExceptionSchemaRich},
    },
)
async def read_aggregate_stats(
    interactor: FromDishka[ReadUserAggregateStatsQueryHandler],
) -> ReadUserAggregateStatsResponseSchema:
    view: UserAggregateStatsView = await interactor()

    return ReadUserAggregateStatsResponseSchema(**asdict(view))
