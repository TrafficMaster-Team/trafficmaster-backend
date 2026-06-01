from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_user_id
from trafficmaster.application.auth.sign_up import SignUpData, SignUpHandler
from trafficmaster.application.common.views.auth.sign_up import SignUpView
from trafficmaster.application.errors.auth import AlreadyAuthenticatedError, AuthenticationError
from trafficmaster.application.errors.user import UserAlreadyExistsError


def _handler(cus: Mock, user_service: Mock, user_gateway: Mock, tx: Mock) -> SignUpHandler:
    return SignUpHandler(
        current_user_service=cus,
        user_service=user_service,
        user_gateway=user_gateway,
        transaction_manager=tx,
    )


def _data() -> SignUpData:
    return SignUpData(email="new@example.com", name="NewUser", password="password123")


async def test_signs_up_successfully(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange: not authenticated yet
    fake_current_user_service.get_current_user.side_effect = AuthenticationError("not authenticated")
    new_user = create_user(user_id=create_user_id())
    fake_user_service.create_user.return_value = new_user
    fake_user_gateway.read_by_email.return_value = None
    handler = _handler(fake_current_user_service, fake_user_service, fake_user_gateway, fake_transaction_manager)

    # Act
    result = await handler(_data())

    # Assert
    assert isinstance(result, SignUpView)
    assert result.id == new_user.id
    fake_user_gateway.add.assert_awaited_once_with(new_user)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_already_authenticated(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange: get_current_user succeeds (default fixture returns a user)
    handler = _handler(fake_current_user_service, fake_user_service, fake_user_gateway, fake_transaction_manager)

    # Act & Assert
    with pytest.raises(AlreadyAuthenticatedError):
        await handler(_data())
    fake_user_gateway.add.assert_not_called()


async def test_fails_when_email_already_exists(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.side_effect = AuthenticationError("not authenticated")
    fake_user_service.create_user.return_value = create_user()
    fake_user_gateway.read_by_email.return_value = create_user(user_id=uuid4())
    handler = _handler(fake_current_user_service, fake_user_service, fake_user_gateway, fake_transaction_manager)

    # Act & Assert
    with pytest.raises(UserAlreadyExistsError):
        await handler(_data())
    fake_user_gateway.add.assert_not_called()
