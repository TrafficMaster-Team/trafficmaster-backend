import pytest
from pydantic import PostgresDsn, ValidationError

from tests.unit.factories.settings_data import (
    create_postgres_settings_data,
    create_sqlalchemy_settings_data,
)
from trafficmaster.setup.config.consts import PORT_MAX, PORT_MIN
from trafficmaster.setup.config.database import (
    POOL_SIZE_MAX,
    POOL_SIZE_MIN,
    PostgresConfig,
    SQLAlchemyConfig,
)


def test_postgres_parses_fields_from_aliases() -> None:
    # Arrange
    data = create_postgres_settings_data(user="alice", db="cards", driver="asyncpg")

    # Act
    sut = PostgresConfig.model_validate(data)

    # Assert
    assert sut.user == "alice"
    assert sut.db_name == "cards"
    assert sut.driver == "asyncpg"


def test_postgres_dsn_builds_valid_uri_from_fields() -> None:
    # Arrange
    data = create_postgres_settings_data(
        user="alice",
        password="secret",
        db="my_db",
        host="db.internal",
        port=5678,
        driver="asyncpg",
    )

    # Act
    sut = PostgresConfig.model_validate(data)

    # Assert
    assert sut.uri == "postgresql+asyncpg://alice:secret@db.internal:5678/my_db"
    assert PostgresDsn(sut.uri)


@pytest.mark.parametrize(
    "port",
    [
        pytest.param(PORT_MIN, id="lower_bound"),
        pytest.param(PORT_MAX, id="upper_bound"),
        pytest.param(5432, id="common_postgres_port"),
    ],
)
def test_postgres_port_accepts_correct_value(port: int) -> None:
    # Arrange
    data = create_postgres_settings_data(port=port)

    # Act & Assert
    assert PostgresConfig.model_validate(data).port == port


@pytest.mark.parametrize(
    "port",
    [
        pytest.param(PORT_MIN - 1, id="too_small"),
        pytest.param(PORT_MAX + 1, id="too_big"),
        pytest.param(0, id="zero"),
    ],
)
def test_postgres_port_rejects_incorrect_value(port: int) -> None:
    data = create_postgres_settings_data(port=port)

    with pytest.raises(ValidationError):
        PostgresConfig.model_validate(data)


def test_sqlalchemy_parses_fields_from_aliases() -> None:
    # Arrange
    data = create_sqlalchemy_settings_data(pool_size=25, echo=True)

    # Act
    sut = SQLAlchemyConfig.model_validate(data)

    # Assert
    assert sut.pool_size == 25
    assert sut.echo is True
    assert sut.expire_on_commit is False


@pytest.mark.parametrize(
    "pool_size",
    [
        pytest.param(POOL_SIZE_MIN, id="lower_bound"),
        pytest.param(POOL_SIZE_MAX, id="upper_bound"),
        pytest.param(10, id="ordinary"),
    ],
)
def test_sqlalchemy_pool_size_accepts_correct_value(pool_size: int) -> None:
    # Arrange
    data = create_sqlalchemy_settings_data(pool_size=pool_size)

    # Act & Assert
    assert SQLAlchemyConfig.model_validate(data).pool_size == pool_size


@pytest.mark.parametrize(
    "pool_size",
    [
        pytest.param(POOL_SIZE_MIN - 1, id="too_small"),
        pytest.param(POOL_SIZE_MAX + 1, id="too_big"),
    ],
)
def test_sqlalchemy_pool_size_rejects_incorrect_value(pool_size: int) -> None:
    data = create_sqlalchemy_settings_data(pool_size=pool_size)

    with pytest.raises(ValidationError):
        SQLAlchemyConfig.model_validate(data)
