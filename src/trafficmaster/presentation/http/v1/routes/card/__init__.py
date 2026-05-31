from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.card.add_tag.handlers import add_tag_route
from trafficmaster.presentation.http.v1.routes.card.change_answer.handlers import change_answer_route
from trafficmaster.presentation.http.v1.routes.card.change_deck.handlers import change_card_deck_route
from trafficmaster.presentation.http.v1.routes.card.change_image.handlers import change_image_route
from trafficmaster.presentation.http.v1.routes.card.change_question.handlers import change_question_route
from trafficmaster.presentation.http.v1.routes.card.create_card.handlers import create_card_route
from trafficmaster.presentation.http.v1.routes.card.delete_card.handlers import delete_card_route
from trafficmaster.presentation.http.v1.routes.card.read.handlers import read_card_route
from trafficmaster.presentation.http.v1.routes.card.read_all.handlers import read_all_cards_route
from trafficmaster.presentation.http.v1.routes.card.remove_tag.handlers import remove_tag_route

card_router = APIRouter(prefix="/card", tags=["Card"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    create_card_route,
    read_all_cards_route,
    read_card_route,
    delete_card_route,
    change_question_route,
    change_answer_route,
    change_card_deck_route,
    change_image_route,
    add_tag_route,
    remove_tag_route,
]

for sub_router in sub_routers:
    card_router.include_router(sub_router)
