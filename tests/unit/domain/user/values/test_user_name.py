import pytest

from trafficmaster.domain.common.errors import DomainFieldError
from trafficmaster.domain.user.errors.user import (
    BadUsernameError,
    TooBigUsernameError,
    TooSmallUsernameError,
    UsernameCantBeEmptyError,
)
from trafficmaster.domain.user.values.user_name import (
    MAX_LENGTH_USERNAME,
    MIN_LENGTH_USERNAME,
    Username,
)


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("a" * MIN_LENGTH_USERNAME, id="min_len"),
        pytest.param("a" * MAX_LENGTH_USERNAME, id="max_len"),
    ],
)
def test_accepts_boundary_length(name: str) -> None:
    sut = Username(name)

    assert sut.name == name


@pytest.mark.parametrize(
    ("name", "expected_error"),
    [
        pytest.param("a" * (MIN_LENGTH_USERNAME - 1), TooSmallUsernameError, id="too_small_len"),
        pytest.param("a" * (MAX_LENGTH_USERNAME + 1), TooBigUsernameError, id="too_big_len"),
        pytest.param("", UsernameCantBeEmptyError, id="empty"),
        pytest.param("    ", UsernameCantBeEmptyError, id="whitespace"),
    ],
)
def test_rejects_out_of_bounds_length(name: str, expected_error: type[DomainFieldError]) -> None:
    with pytest.raises(expected_error):
        Username(name)


@pytest.mark.parametrize(
    "name",
    [
        "username",
        "user.name",
        "user-name",
        "user_name",
        "user123",
        "user.name123",
        "u.ser-name123",
        "u-ser_name",
        "u-ser.name",
    ],
)
def test_accepts_correct_names(name: str) -> None:
    assert Username(name).name == name


@pytest.mark.parametrize(
    "name",
    [
        ".username",
        "-username",
        "_username",
        "username.",
        "username-",
        "username_",
        "user..name",
        "user--name",
        "user__name",
        "user!name",
        "user@name",
        "user#name",
    ],
)
def test_rejects_incorrect_names(name: str) -> None:
    with pytest.raises(BadUsernameError):
        Username(name)


def test_name_str_representation() -> None:
    sut = Username("alice")

    assert str(sut) == "alice"


def test_name_equality() -> None:
    assert Username("alice") == Username("alice")
    assert Username("alice") != Username("bob")
