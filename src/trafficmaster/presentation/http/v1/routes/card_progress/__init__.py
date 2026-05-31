from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.card_progress.deck_stats.handlers import deck_stats_route
from trafficmaster.presentation.http.v1.routes.card_progress.preview_intervals.handlers import preview_intervals_route
from trafficmaster.presentation.http.v1.routes.card_progress.read_progress.handlers import read_progress_route
from trafficmaster.presentation.http.v1.routes.card_progress.reset_progress.handlers import reset_progress_route
from trafficmaster.presentation.http.v1.routes.card_progress.review_card.handlers import review_card_route
from trafficmaster.presentation.http.v1.routes.card_progress.review_log_by_card.handlers import review_log_by_card_route
from trafficmaster.presentation.http.v1.routes.card_progress.review_log_by_user.handlers import review_log_by_user_route
from trafficmaster.presentation.http.v1.routes.card_progress.review_queue.handlers import review_queue_route

card_progress_router = APIRouter(prefix="/review", tags=["Card Progress"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    # Static paths must be registered before the "/card/{card_id}" and "/deck/{deck_id}" groups.
    review_queue_route,
    review_log_by_user_route,
    review_card_route,
    reset_progress_route,
    read_progress_route,
    preview_intervals_route,
    review_log_by_card_route,
    deck_stats_route,
]

for sub_router in sub_routers:
    card_progress_router.include_router(sub_router)
