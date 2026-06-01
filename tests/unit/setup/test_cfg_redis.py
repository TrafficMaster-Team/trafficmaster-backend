import pytest
from pydantic import ValidationError

from tests.unit.factories.settings_data import create_redis_settings_data
from trafficmaster.setup.config.redis import REDIS_MAX_CONNECTION_MIN, RedisConfig


def test_redis_parses_fields_from_aliases() -> None:
    # Arrange
    data = create_redis_settings_data(host="cache.internal", port=6380, cache_db=2)

    # Act
    sut = RedisConfig.model_validate(data)

    # Assert
    assert sut.host == "cache.internal"
    assert sut.port == 6380
    assert sut.cache_db == 2


def test_redis_cache_uri_contains_host_and_port() -> None:
    # Arrange
    data = create_redis_settings_data(host="cache.internal", port=6380, password="pw", cache_db=3)

    # Act
    uri = RedisConfig.model_validate(data).cache_uri

    # Assert
    assert uri.startswith("redis://")
    assert "cache.internal:6380" in uri


def test_redis_max_connections_accepts_minimum() -> None:
    # Arrange
    data = create_redis_settings_data(max_connections=REDIS_MAX_CONNECTION_MIN)

    # Act & Assert
    assert RedisConfig.model_validate(data).max_connections == REDIS_MAX_CONNECTION_MIN


@pytest.mark.parametrize(
    "max_connections",
    [
        pytest.param(REDIS_MAX_CONNECTION_MIN - 1, id="below_min"),
        pytest.param(-5, id="negative"),
    ],
)
def test_redis_max_connections_rejects_too_small(max_connections: int) -> None:
    # Arrange
    data = create_redis_settings_data(max_connections=max_connections)

    # Act & Assert
    with pytest.raises(ValidationError):
        RedisConfig.model_validate(data)
