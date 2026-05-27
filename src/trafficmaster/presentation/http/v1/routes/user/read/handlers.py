from typing import Final

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path

read_router: Final[APIRouter] = APIRouter(tags=["User"], route_class=DishkaRoute)

UserIDPathParameter = Path(
    title="The ID of the user to get",
    description="The ID of the user to get. We using UUID id's",
    examples=["19178bf6-8f84-406e-b213-102ec84fab9f", "75079971-fb0e-4e04-bf07-ceb57faebe84"],
)
