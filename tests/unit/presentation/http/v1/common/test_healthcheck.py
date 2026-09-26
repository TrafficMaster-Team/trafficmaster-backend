from dataclasses import dataclass

import pytest
from fastapi import Response, status

from trafficmaster.application.common.ports.system_health import SystemHealth
from trafficmaster.presentation.http.v1.common.routes.healthcheck import get_readiness


@dataclass(frozen=True, slots=True)
class HealthCheckerStub:
    health: SystemHealth

    async def check(self) -> SystemHealth:
        return self.health


@pytest.mark.parametrize(
    ("database_available", "cache_available", "expected_code", "expected_body"),
    [
        pytest.param(
            True,
            True,
            status.HTTP_200_OK,
            {"status": "ready", "database": "up", "cache": "up"},
            id="ready",
        ),
        pytest.param(
            True,
            False,
            status.HTTP_200_OK,
            {"status": "degraded", "database": "up", "cache": "down"},
            id="cache_degraded",
        ),
        pytest.param(
            False,
            True,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {"status": "not_ready", "database": "down", "cache": "up"},
            id="database_unavailable",
        ),
    ],
)
async def test_readiness_status_depends_on_dependency_health(
    *,
    database_available: bool,
    cache_available: bool,
    expected_code: int,
    expected_body: dict[str, str],
) -> None:
    response = Response()
    checker = HealthCheckerStub(
        SystemHealth(database_available=database_available, cache_available=cache_available),
    )

    result = await get_readiness(response, checker)

    assert response.status_code == expected_code
    assert result.model_dump() == expected_body
