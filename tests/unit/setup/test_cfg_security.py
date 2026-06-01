from datetime import timedelta

import pytest
from pydantic import ValidationError

from tests.unit.factories.settings_data import create_auth_settings_data
from trafficmaster.setup.config.security import AuthSettings


def test_auth_parses_fields_and_converts_ttl_to_timedelta() -> None:
    # Arrange
    data = create_auth_settings_data(jwt_algorithm="HS512", session_ttl_min="30")

    # Act
    sut = AuthSettings.model_validate(data)

    # Assert
    assert sut.jwt_algorithm == "HS512"
    assert sut.session_ttl_min == timedelta(minutes=30)


@pytest.mark.parametrize(
    "ttl",
    [
        pytest.param("abc", id="non_numeric"),
        pytest.param("0", id="below_one_minute"),
    ],
)
def test_auth_rejects_invalid_session_ttl(ttl: str) -> None:
    # Arrange
    data = create_auth_settings_data(session_ttl_min=ttl)

    # Act & Assert
    with pytest.raises(ValidationError):
        AuthSettings.model_validate(data)


@pytest.mark.parametrize(
    "threshold",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(1.0, id="one"),
        pytest.param(1.5, id="above_one"),
    ],
)
def test_auth_rejects_out_of_range_refresh_threshold(threshold: float) -> None:
    # Arrange
    data = create_auth_settings_data(session_refresh_threshold=threshold)

    # Act & Assert
    with pytest.raises(ValidationError):
        AuthSettings.model_validate(data)


def test_auth_rejects_unknown_jwt_algorithm() -> None:
    # Arrange
    data = create_auth_settings_data(jwt_algorithm="XX999")

    # Act & Assert
    with pytest.raises(ValidationError):
        AuthSettings.model_validate(data)
