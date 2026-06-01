from unittest.mock import Mock

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.auth.log_in import LogInData, LogInHandler
from trafficmaster.application.errors.auth import AlreadyAuthenticatedError, AuthenticationError
from trafficmaster.application.errors.user import UserNotFoundByEmailError


def _handler(cus: Mock, user_gateway: Mock, user_service: Mock, auth_service: Mock) -> LogInHandler:
    return LogInHandler(
        current_user_service=cus,
        user_gateway=user_gateway,
        user_service=user_service,
        auth_service=auth_service,
    )


def _data() -> LogInData:
    return LogInData(email="user@example.com", password="password123")


async def test_logs_in_successfully(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_user_service: Mock,
    fake_auth_session_service: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.side_effect = AuthenticationError("not authenticated")
    user = create_user(is_active=True)
    fake_user_gateway.read_by_email.return_value = user
    fake_user_service.verify_password.return_value = True
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_user_service, fake_auth_session_service)

    # Act
    await handler(_data())

    # Assert
    fake_auth_session_service.create_session.assert_awaited_once_with(user.id)


async def test_fails_when_already_authenticated(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_user_service: Mock,
    fake_auth_session_service: Mock,
) -> None:
    # Arrange: default fixture get_current_user returns a user
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_user_service, fake_auth_session_service)

    # Act & Assert
    with pytest.raises(AlreadyAuthenticatedError):
        await handler(_data())


async def test_fails_when_user_not_found(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_user_service: Mock,
    fake_auth_session_service: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.side_effect = AuthenticationError("not authenticated")
    fake_user_gateway.read_by_email.return_value = None
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_user_service, fake_auth_session_service)

    # Act & Assert
    with pytest.raises(UserNotFoundByEmailError):
        await handler(_data())
    fake_auth_session_service.create_session.assert_not_called()


async def test_fails_with_wrong_password(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_user_service: Mock,
    fake_auth_session_service: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.side_effect = AuthenticationError("not authenticated")
    fake_user_gateway.read_by_email.return_value = create_user(is_active=True)
    fake_user_service.verify_password.return_value = False
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_user_service, fake_auth_session_service)

    # Act & Assert
    with pytest.raises(AuthenticationError):
        await handler(_data())
    fake_auth_session_service.create_session.assert_not_called()


async def test_fails_when_account_inactive(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_user_service: Mock,
    fake_auth_session_service: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.side_effect = AuthenticationError("not authenticated")
    fake_user_gateway.read_by_email.return_value = create_user(is_active=False)
    fake_user_service.verify_password.return_value = True
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_user_service, fake_auth_session_service)

    # Act & Assert
    with pytest.raises(AuthenticationError):
        await handler(_data())
    fake_auth_session_service.create_session.assert_not_called()
