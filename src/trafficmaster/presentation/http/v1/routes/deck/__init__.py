from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.deck.assign_config.handlers import assign_config_route
from trafficmaster.presentation.http.v1.routes.deck.change_description.handlers import change_description_route
from trafficmaster.presentation.http.v1.routes.deck.change_privacy.handlers import change_privacy_route
from trafficmaster.presentation.http.v1.routes.deck.change_title.handlers import change_title_route
from trafficmaster.presentation.http.v1.routes.deck.copy_deck.handlers import copy_deck_route
from trafficmaster.presentation.http.v1.routes.deck.create_deck.handlers import create_deck_route
from trafficmaster.presentation.http.v1.routes.deck.delete_deck.handlers import delete_deck_route
from trafficmaster.presentation.http.v1.routes.deck.read.handlers import read_deck_route
from trafficmaster.presentation.http.v1.routes.deck.read_public.handlers import read_public_decks_route
from trafficmaster.presentation.http.v1.routes.deck.read_user_decks.handlers import read_user_decks_route

deck_router = APIRouter(prefix="/deck", tags=["Deck"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    create_deck_route,
    read_user_decks_route,
    # Static paths must be registered before "/{deck_id}" so they aren't swallowed by the path param.
    read_public_decks_route,
    read_deck_route,
    delete_deck_route,
    change_title_route,
    change_description_route,
    change_privacy_route,
    assign_config_route,
    copy_deck_route,
]

for sub_router in sub_routers:
    deck_router.include_router(sub_router)
