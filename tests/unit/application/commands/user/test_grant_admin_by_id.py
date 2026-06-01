from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.user.grant_admin_by_id import (
    GrantAdminByIdCommand,
    GrantAdminByIdCommandHandler,
)
from trafficmaster.application.errors.user import UserNotFoundByIdError


def _handler(cus: Mock, us: Mock, acl: Mock, gw: Mock, tx: Mock) -> GrantAdminByIdCommandHandler:
    return GrantAdminByIdCommandHandler(
        current_user_service=cus,
        user_service=us,
        access_service=acl,
        user_gateway=gw,
        transaction_manager=tx,
    )


async def test_grants_admin_successfully(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    target = create_user()
    fake_user_gateway.read_by_id.return_value = target
    handler = _handler(
        fake_current_user_service, fake_user_service, fake_access_service, fake_user_gateway, fake_transaction_manager
    )

    # Act
    await handler(GrantAdminByIdCommand(user_id=uuid4()))

    # Assert
    fake_access_service.toggle_admin_role.assert_called_once_with(target, is_admin=True)
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
        await handler(GrantAdminByIdCommand(user_id=uuid4()))
    fake_access_service.toggle_admin_role.assert_not_called()
