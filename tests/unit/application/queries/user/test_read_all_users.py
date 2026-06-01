from unittest.mock import Mock

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.views.user.read_user_by_id import ReadUserByIDView
from trafficmaster.application.errors.user import NoPermissionToManageUserError
from trafficmaster.application.queries.user.read_all_users import (
    ReadAllUsersQuery,
    ReadAllUsersQueryHandler,
)
from trafficmaster.domain.user.values.user_role import UserRole


def _handler(cus: Mock, gw: Mock, acl: Mock) -> ReadAllUsersQueryHandler:
    return ReadAllUsersQueryHandler(current_user_service=cus, user_gateway=gw, access_service=acl)


def _query() -> ReadAllUsersQuery:
    return ReadAllUsersQuery(limit=10, offset=0, sorting_field="name", sorting_order=SortingOrder.ASC)


async def test_reads_all_users_for_admin(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.return_value = create_user(role=UserRole.ADMIN)
    fake_user_gateway.read_all_users.return_value = [create_user(), create_user()]
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_access_service)

    # Act
    result = await handler(_query())

    # Assert
    assert len(result) == 2
    assert all(isinstance(view, ReadUserByIDView) for view in result)


async def test_fails_for_regular_user(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.return_value = create_user(role=UserRole.USER)
    handler = _handler(fake_current_user_service, fake_user_gateway, fake_access_service)

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(_query())
    fake_user_gateway.read_all_users.assert_not_called()
