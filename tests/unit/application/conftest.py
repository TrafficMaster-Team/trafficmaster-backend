from typing import cast
from unittest.mock import AsyncMock, Mock, create_autospec

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService


@pytest.fixture
def fake_transaction_manager() -> Mock:
    fake = Mock()
    fake.commit = AsyncMock()
    fake.flush = AsyncMock()
    fake.rollback = AsyncMock()
    return fake


@pytest.fixture
def fake_user_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    fake.read_by_email = AsyncMock(return_value=None)
    fake.read_all_users = AsyncMock(return_value=[])
    return fake


@pytest.fixture
def fake_current_user_service() -> Mock:
    fake = Mock()
    fake.get_current_user = AsyncMock(return_value=create_user())
    return fake


@pytest.fixture
def fake_user_service() -> Mock:
    return cast("Mock", create_autospec(UserService))


@pytest.fixture
def fake_access_service() -> Mock:
    fake = cast("Mock", create_autospec(AccessService))
    fake.can_manage_user.return_value = True
    return fake
