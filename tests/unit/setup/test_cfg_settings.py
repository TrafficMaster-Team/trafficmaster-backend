from collections.abc import Callable
from typing import Any

import pytest
from pydantic import ValidationError

from tests.unit.factories.settings_data import (
    create_asgi_settings_data,
    create_auth_settings_data,
    create_postgres_settings_data,
    create_redis_settings_data,
    create_sqlalchemy_settings_data,
)
from trafficmaster.setup.config.settings import AppConfig


def create_app_config_data() -> dict[str, Any]:
    return {
        "APP_ENV": "production",
        "postgres": create_postgres_settings_data(),
        "sqlalchemy": create_sqlalchemy_settings_data(),
        "redis": create_redis_settings_data(),
        "asgi": create_asgi_settings_data(
            FASTAPI_DEBUG=False,
            FASTAPI_ALLOW_CREDENTIALS=True,
            CORS_ALLOWED_ORIGINS="https://trafficmaster.example.com",
            TRUSTED_HOSTS="api.trafficmaster.example.com",
        ),
        "security": {
            "auth": create_auth_settings_data(jwt_secret="j" * 32),
            "cookies": {"SECURE": True, "COOKIE_SAME_SITE": "strict"},
            "password": {"PEPPER": "p" * 32},
        },
    }


def test_production_config_accepts_safe_settings() -> None:
    config = AppConfig.model_validate(create_app_config_data())

    assert config.environment == "production"


@pytest.mark.parametrize(
    ("make_unsafe", "expected_error"),
    [
        pytest.param(
            lambda data: data["asgi"].update({"FASTAPI_DEBUG": True}),
            "FASTAPI_DEBUG must be false",
            id="debug",
        ),
        pytest.param(
            lambda data: data["security"]["cookies"].update({"SECURE": False}),
            "SECURE must be true",
            id="insecure_cookie",
        ),
        pytest.param(
            lambda data: data["security"]["auth"].update({"JWT_SECRET": "short"}),
            "JWT_SECRET must contain at least 32 characters",
            id="short_jwt_secret",
        ),
        pytest.param(
            lambda data: data["security"]["password"].update({"PEPPER": "short"}),
            "PEPPER must contain at least 32 characters",
            id="short_pepper",
        ),
        pytest.param(
            lambda data: data["asgi"].update({"CORS_ALLOWED_ORIGINS": "http://trafficmaster.example.com"}),
            "CORS_ALLOWED_ORIGINS must contain only explicit HTTPS origins",
            id="insecure_origin",
        ),
        pytest.param(
            lambda data: data["asgi"].update({"TRUSTED_HOSTS": "*"}),
            "TRUSTED_HOSTS must contain an explicit host allowlist",
            id="wildcard_trusted_hosts",
        ),
    ],
)
def test_production_config_rejects_unsafe_settings(
    make_unsafe: Callable[[dict[str, Any]], None],
    expected_error: str,
) -> None:
    data = create_app_config_data()
    make_unsafe(data)

    with pytest.raises(ValidationError, match=expected_error):
        AppConfig.model_validate(data)
