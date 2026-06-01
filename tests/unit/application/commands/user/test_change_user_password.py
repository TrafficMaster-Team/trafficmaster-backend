from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.user.change_user_password import (
    ChangeUserPasswordCommand,
    ChangeUserPasswordCommandHandler,
)
from trafficmaster.application.errors.user import UserNotFoundByIdError


def _handler(cus: Mock, us: Mock, gw: Mock, acl: Mock, tx: Mock) -> ChangeUserPasswordCommandHandler:
    return ChangeUserPasswordCommandHandler(
        current_user_service=cus,
        user_service=us,
        user_gateway=gw,
        access_service=acl,
        transaction_manager=tx,
    )


async def test_changes_password_successfully(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_user_gateway, fake_access_service, fake_transaction_manager
    )

    # Act
    await handler(ChangeUserPasswordCommand(user_id=uuid4(), password="newpassword1"))

    # Assert
    fake_user_service.change_password.assert_called_once()
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_user_not_found(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_user_gateway, fake_access_service, fake_transaction_manager
    )

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(ChangeUserPasswordCommand(user_id=uuid4(), password="newpassword1"))
    fake_user_service.change_password.assert_not_called()
