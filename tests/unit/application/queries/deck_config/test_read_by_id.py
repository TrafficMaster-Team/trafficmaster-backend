from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_deck_config_name
from trafficmaster.application.common.views.deck_config.read_by_id import ReadDeckConfigByIDView
from trafficmaster.application.errors.deck import DeckConfigNotFoundError
from trafficmaster.application.queries.deck_config.read_by_id import (
    ReadDeckConfigByIdQuery,
    ReadDeckConfigByIdQueryHandler,
)


def _handler(cus: Mock, acl: Mock, gw: Mock, user_gateway: Mock) -> ReadDeckConfigByIdQueryHandler:
    return ReadDeckConfigByIdQueryHandler(
        current_user_service=cus,
        access_service=acl,
        deck_config_gateway=gw,
        user_gateway=user_gateway,
    )


async def test_reads_deck_config_successfully(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    config = create_deck_config(name=create_deck_config_name("Custom"))
    fake_deck_config_gateway.read_by_id.return_value = config
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_config_gateway, fake_user_gateway)

    # Act
    result = await handler(ReadDeckConfigByIdQuery(deck_config_id=config.id))

    # Assert
    assert isinstance(result, ReadDeckConfigByIDView)
    assert result.id == config.id
    assert result.name == "Custom"


async def test_fails_when_config_not_found(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_config_gateway.read_by_id.return_value = None
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_config_gateway, fake_user_gateway)

    # Act & Assert
    with pytest.raises(DeckConfigNotFoundError):
        await handler(ReadDeckConfigByIdQuery(deck_config_id=uuid4()))
