import pytest

from trafficmaster.domain.user.errors.user import WrongUserEmailFormatError
from trafficmaster.domain.user.values.user_email import UserEmail


@pytest.mark.parametrize(
    "email",
    [
        pytest.param("alice@example.com", id="simple_email"),
        pytest.param("bob.smith@example.com", id="with_dot"),
        pytest.param("user_name@example.co.uk", id="with_underscore"),
        pytest.param("test123@test-domain.org", id="with_numbers_and_hyphen"),
        pytest.param("user+tag@example.com", id="with_plus"),
        pytest.param("user%tag@example.com", id="with_percent"),
        pytest.param("user-name@example.com", id="with_hyphen"),
        pytest.param("a@b.co", id="minimal_valid"),
        pytest.param("UPPERCASE@EXAMPLE.COM", id="uppercase"),
        pytest.param("MixedCase@Example.Com", id="mixed_case"),
    ],
)
def test_accepts_valid_email(email: str) -> None:
    # Arrange & Act
    sut = UserEmail(email)

    # Assert
    assert sut.email == email
    assert str(sut) == email


@pytest.mark.parametrize(
    "email",
    [
        pytest.param("", id="empty"),
        pytest.param("invalid", id="no_at_symbol"),
        pytest.param("@example.com", id="missing_local_part"),
        pytest.param("user@", id="missing_domain"),
        pytest.param("user@example", id="missing_tld"),
        pytest.param("user@.com", id="domain_starts_with_dot"),
        pytest.param("user@example.", id="domain_ends_with_dot"),
        pytest.param("user@@example.com", id="double_at"),
        pytest.param("user @example.com", id="space_in_email"),
        pytest.param("user@exam ple.com", id="space_in_domain"),
        pytest.param("user.@example.com.", id="ends_with_dot"),
        pytest.param("user..name@example.com", id="consecutive_dots"),
        pytest.param("user@example..com", id="consecutive_dots_in_domain"),
        pytest.param("user@exam#ple.com", id="invalid_char_in_domain"),
        pytest.param("user#name@example.com", id="invalid_char_in_local"),
    ],
)
def test_rejects_invalid_email(email: str) -> None:
    # Arrange & Act & Assert
    with pytest.raises(WrongUserEmailFormatError):
        UserEmail(email)


def test_email_equality() -> None:
    # Arrange
    email = "alice@example.com"

    # Assert
    assert UserEmail(email) == UserEmail(email)
    assert hash(UserEmail(email)) == hash(UserEmail(email))


def test_email_inequality() -> None:
    # Assert
    assert UserEmail("alice@example.com") != UserEmail("bob@example.com")


def test_email_str_representation() -> None:
    # Arrange
    sut = UserEmail("alice@example.com")

    # Act & Assert
    assert str(sut) == "alice@example.com"
