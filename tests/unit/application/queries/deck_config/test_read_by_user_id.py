from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.views.deck_config.read_by_id import ReadDeckConfigByIDView
from trafficmaster.application.errors.user import UserNotFoundByIdError
from trafficmaster.application.queries.deck_config.read_by_user_id import (
    ReadDeckConfigsByUserIdQuery,
    ReadDeckConfigsByUserIdQueryHandler,
)


def _handler(cus: Mock, acl: Mock, gw: Mock, user_gateway: Mock) -> ReadDeckConfigsByUserIdQueryHandler:
    return ReadDeckConfigsByUserIdQueryHandler(
        current_user_service=cus,
        access_service=acl,
        deck_config_gateway=gw,
        user_gateway=user_gateway,
    )


async def test_reads_configs_by_user(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_user_id.return_value = [create_deck_config(), create_deck_config()]
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_config_gateway, fake_user_gateway)

    # Act
    result = await handler(ReadDeckConfigsByUserIdQuery(user_id=uuid4()))

    # Assert
    assert len(result) == 2
    assert all(isinstance(view, ReadDeckConfigByIDView) for view in result)


async def test_fails_when_user_not_found(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = None
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_config_gateway, fake_user_gateway)

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(ReadDeckConfigsByUserIdQuery(user_id=uuid4()))
