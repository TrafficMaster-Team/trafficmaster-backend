from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_user_email, create_user_id, create_username
from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.application.queries.user.read_by_id import (
    ReadUserByIdQuery,
    ReadUserByIdQueryHandler,
)
from trafficmaster.domain.user.values.user_role import UserRole


def _handler(cus: Mock, gw: Mock, acl: Mock) -> ReadUserByIdQueryHandler:
    return ReadUserByIdQueryHandler(current_user_service=cus, user_gateway=gw, access_service=acl)


async def test_reads_user_by_id_successfully(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    user = create_user(
        username=create_username("Alice"),
        email=create_user_email("alice@example.com"),
        role=UserRole.ADMIN,
    )
    fake_user_gateway.read_by_id.return_value = user
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_access_service)

    # Act
    result = await handler(ReadUserByIdQuery(user_id=user.id))

    # Assert
    assert isinstance(result, ReadUserByIDView)
    assert result.id == user.id
    assert result.name == "Alice"
    assert result.email == "alice@example.com"
    assert result.role == UserRole.ADMIN


async def test_fails_when_user_not_found(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = None
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_access_service)

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(ReadUserByIdQuery(user_id=uuid4()))


async def test_fails_when_no_permission(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user(user_id=create_user_id())
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_access_service)

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(ReadUserByIdQuery(user_id=uuid4()))
