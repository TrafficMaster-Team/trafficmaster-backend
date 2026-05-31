from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.auth.log_in.handlers import log_in_route
from trafficmaster.presentation.http.v1.routes.auth.log_out.handlers import log_out_route
from trafficmaster.presentation.http.v1.routes.auth.read_current_user.handlers import read_current_user_route
from trafficmaster.presentation.http.v1.routes.auth.sign_up.handlers import sign_up_route

auth_router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    sign_up_route,
    log_in_route,
    log_out_route,
    read_current_user_route,
]

for sub_router in sub_routers:
    auth_router.include_router(sub_router)
