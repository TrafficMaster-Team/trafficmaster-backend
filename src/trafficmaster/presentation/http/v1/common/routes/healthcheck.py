from typing import Literal

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from trafficmaster.application.common.ports.system_health import SystemHealthChecker

router: APIRouter = APIRouter(
    prefix="/healthcheck",
    tags=["healthcheck"],
    route_class=DishkaRoute,
)


class LivenessResponseSchema(BaseModel):
    status: Literal["alive"] = "alive"


class ReadinessResponseSchema(BaseModel):
    status: Literal["ready", "degraded", "not_ready"]
    database: Literal["up", "down"]
    cache: Literal["up", "down"]


@router.get("/live", status_code=status.HTTP_200_OK)
async def get_liveness() -> LivenessResponseSchema:
    return LivenessResponseSchema()


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponseSchema}},
)
async def get_readiness(
    response: Response,
    health_checker: FromDishka[SystemHealthChecker],
) -> ReadinessResponseSchema:
    health = await health_checker.check()

    if not health.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        readiness_status = "not_ready"
    elif not health.cache_available:
        readiness_status = "degraded"
    else:
        readiness_status = "ready"

    return ReadinessResponseSchema(
        status=readiness_status,
        database="up" if health.database_available else "down",
        cache="up" if health.cache_available else "down",
    )
