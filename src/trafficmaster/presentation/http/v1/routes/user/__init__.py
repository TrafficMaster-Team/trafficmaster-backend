from collections.abc import Iterable

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from trafficmaster.presentation.http.v1.routes.user.activate_user.handlers import activate_user_route
from trafficmaster.presentation.http.v1.routes.user.change_user_email.handlers import change_user_email_route
from trafficmaster.presentation.http.v1.routes.user.change_user_name.handlers import change_username_router
from trafficmaster.presentation.http.v1.routes.user.change_user_password.handlers import change_user_password_route
from trafficmaster.presentation.http.v1.routes.user.create_user.handlers import create_user_route
from trafficmaster.presentation.http.v1.routes.user.delete_user.handlers import delete_user_route
from trafficmaster.presentation.http.v1.routes.user.grant_admin.handlers import grant_admin_route
from trafficmaster.presentation.http.v1.routes.user.read.handlers import read_router
from trafficmaster.presentation.http.v1.routes.user.read_aggregate_stats.handlers import read_aggregate_stats_router
from trafficmaster.presentation.http.v1.routes.user.read_all.handlers import read_all_router
from trafficmaster.presentation.http.v1.routes.user.revoke_admin.handlers import revoke_admin_route

user_router = APIRouter(prefix="/user", tags=["User"], route_class=DishkaRoute)

sub_routers: Iterable[APIRouter] = [
    read_all_router,
    # Static paths must be registered before "/{user_id}" so they aren't swallowed by the path param.
    read_aggregate_stats_router,
    create_user_route,
    read_router,
    delete_user_route,
    grant_admin_route,
    revoke_admin_route,
    change_user_password_route,
    activate_user_route,
    change_username_router,
    change_user_email_route,
]

for sub_router in sub_routers:
    user_router.include_router(sub_router)
