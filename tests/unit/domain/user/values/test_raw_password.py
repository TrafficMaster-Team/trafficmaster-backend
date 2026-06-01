import pytest

from trafficmaster.domain.user.errors.password import (
    PasswordCantBeEmptyError,
    WeakPasswordWasProvidedError,
)
from trafficmaster.domain.user.values.raw_password import (
    MAX_LENGTH_PASSWORD,
    MIN_LENGTH_PASSWORD,
    RawPassword,
)


@pytest.mark.parametrize(
    "password",
    [
        pytest.param("abcdefg1", id="min_len"),
        pytest.param("Password1", id="typical"),
        pytest.param("a" * (MAX_LENGTH_PASSWORD - 1) + "1", id="max_len"),
    ],
)
def test_accepts_valid_password(password: str) -> None:
    sut = RawPassword(password)

    assert sut.value == password


@pytest.mark.parametrize(
    ("password", "expected_error"),
    [
        pytest.param("", PasswordCantBeEmptyError, id="empty"),
        pytest.param(" " * MIN_LENGTH_PASSWORD, PasswordCantBeEmptyError, id="whitespace"),
        pytest.param("12345678", WeakPasswordWasProvidedError, id="only_digits"),
        pytest.param("abcdefgh", WeakPasswordWasProvidedError, id="only_letters"),
        pytest.param("abc123", WeakPasswordWasProvidedError, id="too_short"),
        pytest.param("a" * (MAX_LENGTH_PASSWORD + 1) + "1", WeakPasswordWasProvidedError, id="too_long"),
    ],
)
def test_rejects_invalid_password(password: str, expected_error: type[Exception]) -> None:
    with pytest.raises(expected_error):
        RawPassword(password)


def test_password_str_is_masked() -> None:
    sut = RawPassword("Password1")

    assert str(sut) == "*" * len("Password1")
