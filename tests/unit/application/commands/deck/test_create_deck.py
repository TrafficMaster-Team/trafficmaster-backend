from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_user_id
from trafficmaster.application.commands.deck.create_deck import CreateDeckCommand, CreateDeckCommandHandler
from trafficmaster.application.common.views.deck.create_deck import CreateDeckView
from trafficmaster.application.errors.deck import DeckConfigNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError


def _handler(
    cus: Mock,
    user_gateway: Mock,
    access_service: Mock,
    tx: Mock,
    deck_gateway: Mock,
    deck_config_gateway: Mock,
    deck_service: Mock,
) -> CreateDeckCommandHandler:
    return CreateDeckCommandHandler(
        current_user_service=cus,
        user_gateway=user_gateway,
        access_service=access_service,
        transaction_manager=tx,
        deck_gateway=deck_gateway,
        deck_config_gateway=deck_config_gateway,
        deck_service=deck_service,
    )


async def test_creates_deck_successfully(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_deck_service: Mock,
) -> None:
    # Arrange
    owner = create_user(user_id=create_user_id())
    created = create_deck()
    fake_user_gateway.read_by_id.return_value = owner
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config(owner_id=owner.id)
    fake_deck_service.create_deck.return_value = created
    handler = _handler(
        fake_current_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_deck_service,
    )

    # Act
    result = await handler(
        CreateDeckCommand(owner_id=owner.id, deck_config_id=uuid4(), title="My Deck", description="d"),
    )

    # Assert
    assert isinstance(result, CreateDeckView)
    assert result.id == created.id
    fake_deck_gateway.add.assert_awaited_once_with(created)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_deck_config_not_found(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_deck_service: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_deck_service,
    )

    # Act & Assert
    with pytest.raises(DeckConfigNotFoundError):
        await handler(CreateDeckCommand(owner_id=uuid4(), deck_config_id=uuid4(), title="My Deck"))
    fake_deck_gateway.add.assert_not_called()


async def test_fails_when_config_belongs_to_another_user(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_deck_service: Mock,
) -> None:
    # Arrange: deck config owned by a different user
    owner = create_user(user_id=create_user_id())
    fake_user_gateway.read_by_id.return_value = owner
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config(owner_id=create_user_id())
    handler = _handler(
        fake_current_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_deck_service,
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(CreateDeckCommand(owner_id=owner.id, deck_config_id=uuid4(), title="My Deck"))
