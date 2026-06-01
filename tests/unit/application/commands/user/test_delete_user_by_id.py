from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.user.delete_user_by_id import (
    DeleteUserByIdCommand,
    DeleteUserByIdCommandHandler,
)
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError


def _handler(cus: Mock, us: Mock, acl: Mock, gw: Mock, tx: Mock) -> DeleteUserByIdCommandHandler:
    return DeleteUserByIdCommandHandler(
        current_user_service=cus,
        user_service=us,
        access_service=acl,
        user_gateway=gw,
        transaction_manager=tx,
    )


async def test_deletes_user_successfully(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_access_service, fake_user_gateway, fake_transaction_manager
    )
    command = DeleteUserByIdCommand(user_id=uuid4())

    # Act
    await handler(command)

    # Assert
    fake_user_gateway.delete_by_id.assert_awaited_once()
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
        fake_current_user_service, fake_user_service, fake_access_service, fake_user_gateway, fake_transaction_manager
    )

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(DeleteUserByIdCommand(user_id=uuid4()))
    fake_user_gateway.delete_by_id.assert_not_called()


async def test_fails_when_no_permission(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_access_service, fake_user_gateway, fake_transaction_manager
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(DeleteUserByIdCommand(user_id=uuid4()))
    fake_user_gateway.delete_by_id.assert_not_called()
