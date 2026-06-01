from unittest.mock import Mock

from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_user_email, create_username
from trafficmaster.application.auth.read_current_user import ReadCurrentUserHandler
from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView
from trafficmaster.domain.user.values.user_role import UserRole


async def test_reads_current_user(fake_current_user_service: Mock) -> None:
    # Arrange
    user = create_user(
        username=create_username("Alice"),
        email=create_user_email("alice@example.com"),
        role=UserRole.ADMIN,
    )
    fake_current_user_service.get_current_user.return_value = user
    handler = ReadCurrentUserHandler(current_user_service=fake_current_user_service)

    # Act
    result = await handler()

    # Assert
    assert isinstance(result, ReadUserByIDView)
    assert result.id == user.id
    assert result.name == "Alice"
    assert result.email == "alice@example.com"
    assert result.role == UserRole.ADMIN
