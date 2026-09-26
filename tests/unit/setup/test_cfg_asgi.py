import pytest
from pydantic import ValidationError

from trafficmaster.setup.config.asgi import ASGIConfig


def test_asgi_uses_defaults_when_empty() -> None:
    # Act
    sut = ASGIConfig.model_validate({})

    # Assert
    assert sut.host == "0.0.0.0"  # noqa: S104
    assert sut.port == 8000
    assert sut.fastapi_debug is False
    assert sut.allow_credentials is False


def test_asgi_overrides_port_from_alias() -> None:
    # Act
    sut = ASGIConfig.model_validate({"UVICORN_PORT": 9000})

    # Assert
    assert sut.port == 9000


def test_asgi_has_default_cors_lists() -> None:
    # Act
    sut = ASGIConfig.model_validate({})

    # Assert
    assert sut.allow_origins == []
    assert sut.allow_methods == ["GET", "POST", "PUT", "PATCH", "DELETE"]
    assert sut.allow_headers == ["Content-Type"]
    assert sut.trusted_hosts == ["*"]
    assert sut.expose_api_docs is True


def test_asgi_rejects_wildcard_origin_with_credentials() -> None:
    with pytest.raises(ValidationError, match="wildcard origin"):
        ASGIConfig.model_validate(
            {
                "FASTAPI_ALLOW_CREDENTIALS": True,
                "CORS_ALLOWED_ORIGINS": "*",
            },
        )


def test_asgi_parses_trusted_hosts() -> None:
    config = ASGIConfig.model_validate({"TRUSTED_HOSTS": "api.example.com, admin.example.com"})

    assert config.trusted_hosts == ["api.example.com", "admin.example.com"]
