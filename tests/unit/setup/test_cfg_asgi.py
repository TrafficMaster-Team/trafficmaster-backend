from trafficmaster.setup.config.asgi import ASGIConfig


def test_asgi_uses_defaults_when_empty() -> None:
    # Act
    sut = ASGIConfig.model_validate({})

    # Assert
    assert sut.host == "0.0.0.0"  # noqa: S104
    assert sut.port == 8000
    assert sut.fastapi_debug is True
    assert sut.allow_credentials is True


def test_asgi_overrides_port_from_alias() -> None:
    # Act
    sut = ASGIConfig.model_validate({"UVICORN_PORT": 9000})

    # Assert
    assert sut.port == 9000


def test_asgi_has_default_cors_lists() -> None:
    # Act
    sut = ASGIConfig.model_validate({})

    # Assert
    assert sut.allow_origins == ["http://localhost:3000"]
    assert sut.allow_methods == ["GET", "POST", "PUT", "PATCH", "DELETE"]
    assert sut.allow_headers == ["Content-Type"]
