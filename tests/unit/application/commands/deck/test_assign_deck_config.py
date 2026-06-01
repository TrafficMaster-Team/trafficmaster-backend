from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_deck_config_id, create_user_id
from trafficmaster.application.commands.deck.assign_deck_config import (
    AssignDeckConfigCommand,
    AssignDeckConfigCommandHandler,
)
from trafficmaster.application.errors.user import NoPermissionToManageUserError


def _handler(
    deck_gateway: Mock,
    deck_config_gateway: Mock,
    user_gateway: Mock,
    tx: Mock,
    cus: Mock,
    acl: Mock,
) -> AssignDeckConfigCommandHandler:
    return AssignDeckConfigCommandHandler(
        deck_gateway=deck_gateway,
        deck_config_gateway=deck_config_gateway,
        user_gateway=user_gateway,
        transaction_manager=tx,
        current_user_service=cus,
        access_service=acl,
    )


async def test_assigns_deck_config_successfully(
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange: config and deck owned by the same user
    owner_id = create_user_id()
    deck = create_deck(owner_id=owner_id)
    new_config = create_deck_config(config_id=create_deck_config_id(), owner_id=owner_id)
    fake_deck_gateway.read_by_id.return_value = deck
    fake_user_gateway.read_by_id.return_value = create_user(user_id=owner_id)
    fake_deck_config_gateway.read_by_id.return_value = new_config
    handler = _handler(
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act
    await handler(AssignDeckConfigCommand(deck_id=uuid4(), deck_config_id=uuid4()))

    # Assert
    assert deck.deck_config_id == new_config.id
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_config_belongs_to_another_owner(
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange: deck owner and config owner differ
    deck = create_deck(owner_id=create_user_id())
    fake_deck_gateway.read_by_id.return_value = deck
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config(owner_id=create_user_id())
    handler = _handler(
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(AssignDeckConfigCommand(deck_id=uuid4(), deck_config_id=uuid4()))
