from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.user.read.handlers import read_router

user_router = APIRouter(prefix="/user", tags=["User"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    read_router,
]

for sub_router in sub_routers:
    user_router.include_router(sub_router)
