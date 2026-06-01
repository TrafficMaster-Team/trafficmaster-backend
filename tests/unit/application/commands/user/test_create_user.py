from unittest.mock import Mock

import pytest

from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_user_email, create_user_id, create_username
from trafficmaster.application.commands.user.create_user import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from trafficmaster.application.common.views.user.create_user import CreateUserView
from trafficmaster.application.errors.user import (
    NoPermissionToManageUserError,
    UserAlreadyExistsError,
)
from trafficmaster.domain.user.values.user_role import UserRole


def _handler(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> CreateUserCommandHandler:
    return CreateUserCommandHandler(
        current_user_service=fake_current_user_service,
        user_service=fake_user_service,
        user_gateway=fake_user_gateway,
        access_service=fake_access_service,
        transaction_manager=fake_transaction_manager,
    )


@pytest.mark.parametrize(
    ("email", "username", "role"),
    [
        pytest.param("user1@example.com", "UserOne", UserRole.USER, id="regular_user"),
        pytest.param("user2@example.com", "UserTwo", UserRole.ADMIN, id="admin_user"),
    ],
)
async def test_creates_user_successfully(
    email: str,
    username: str,
    role: UserRole,
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    new_user = create_user(
        user_id=create_user_id(),
        username=create_username(username),
        email=create_user_email(email),
        role=role,
    )
    fake_user_service.create_user.return_value = new_user
    fake_user_gateway.read_by_email.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
    )

    # Act
    result = await handler(CreateUserCommand(email=email, username=username, password="password123", role=role))

    # Assert
    assert isinstance(result, CreateUserView)
    assert result.id == new_user.id
    fake_user_gateway.add.assert_awaited_once_with(new_user)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_email_already_exists(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_email.return_value = create_user()
    handler = _handler(
        fake_current_user_service,
        fake_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
    )

    # Act & Assert
    with pytest.raises(UserAlreadyExistsError):
        await handler(CreateUserCommand(email="taken@example.com", username="Name", password="password123"))

    fake_user_gateway.add.assert_not_called()
    fake_transaction_manager.commit.assert_not_called()


async def test_fails_when_no_permission(
    fake_current_user_service: Mock,
    fake_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_email.return_value = None
    fake_user_service.create_user.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service,
        fake_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(CreateUserCommand(email="new@example.com", username="Name", password="password123"))

    fake_user_gateway.add.assert_not_called()
    fake_transaction_manager.commit.assert_not_called()
