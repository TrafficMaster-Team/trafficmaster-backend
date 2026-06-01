from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.user.change_user_email import (
    ChangeUserEmailCommand,
    ChangeUserEmailCommandHandler,
)
from trafficmaster.application.errors.user import (
    EmailAlreadyExistsError,
    NoPermissionToManageUserError,
    UserNotFoundByIdError,
)


def _handler(cus: Mock, us: Mock, gw: Mock, acl: Mock, tx: Mock) -> ChangeUserEmailCommandHandler:
    return ChangeUserEmailCommandHandler(
        current_user_service=cus,
        user_service=us,
        user_gateway=gw,
        access_service=acl,
        transaction_manager=tx,
    )


async def test_changes_email_successfully(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    target = create_user()
    fake_user_gateway.read_by_email.return_value = None
    fake_user_gateway.read_by_id.return_value = target
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_user_gateway, fake_access_service, fake_transaction_manager
    )

    # Act
    await handler(ChangeUserEmailCommand(user_id=uuid4(), email="new@example.com"))

    # Assert
    fake_user_service.change_email.assert_called_once()
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_email_taken(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_email.return_value = create_user()
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_user_gateway, fake_access_service, fake_transaction_manager
    )

    # Act & Assert
    with pytest.raises(EmailAlreadyExistsError):
        await handler(ChangeUserEmailCommand(user_id=uuid4(), email="taken@example.com"))
    fake_transaction_manager.commit.assert_not_called()


async def test_fails_when_user_not_found(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_email.return_value = None
    fake_user_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_user_gateway, fake_access_service, fake_transaction_manager
    )

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(ChangeUserEmailCommand(user_id=uuid4(), email="new@example.com"))


async def test_fails_when_no_permission(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_email.return_value = None
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_user_gateway, fake_access_service, fake_transaction_manager
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(ChangeUserEmailCommand(user_id=uuid4(), email="new@example.com"))
    fake_user_service.change_email.assert_not_called()
