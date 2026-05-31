from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.deck_config.change_advanced.handlers import change_advanced_route
from trafficmaster.presentation.http.v1.routes.deck_config.change_daily_limits.handlers import change_daily_limits_route
from trafficmaster.presentation.http.v1.routes.deck_config.change_lapses.handlers import change_lapses_route
from trafficmaster.presentation.http.v1.routes.deck_config.change_name.handlers import change_name_route
from trafficmaster.presentation.http.v1.routes.deck_config.change_new_cards.handlers import change_new_cards_route
from trafficmaster.presentation.http.v1.routes.deck_config.create_deck_config.handlers import create_deck_config_route
from trafficmaster.presentation.http.v1.routes.deck_config.delete_deck_config.handlers import delete_deck_config_route
from trafficmaster.presentation.http.v1.routes.deck_config.read.handlers import read_deck_config_route
from trafficmaster.presentation.http.v1.routes.deck_config.read_user_configs.handlers import read_user_configs_route

deck_config_router = APIRouter(prefix="/deck-config", tags=["Deck Config"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    create_deck_config_route,
    read_user_configs_route,
    read_deck_config_route,
    delete_deck_config_route,
    change_name_route,
    change_daily_limits_route,
    change_new_cards_route,
    change_advanced_route,
    change_lapses_route,
]

for sub_router in sub_routers:
    deck_config_router.include_router(sub_router)
