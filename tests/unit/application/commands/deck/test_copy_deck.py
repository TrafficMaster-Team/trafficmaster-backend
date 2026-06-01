from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck.copy_deck import CopyDeckCommand, CopyDeckCommandHandler
from trafficmaster.application.common.views.deck.copy_deck import CopyDeckView
from trafficmaster.application.errors.deck import DeckNotFoundError


def _handler(
    tx: Mock,
    cus: Mock,
    deck_gateway: Mock,
    deck_config_gateway: Mock,
    card_gateway: Mock,
    user_gateway: Mock,
    access_service: Mock,
    deck_service: Mock,
    deck_config_service: Mock,
    card_service: Mock,
) -> CopyDeckCommandHandler:
    return CopyDeckCommandHandler(
        transaction_manager=tx,
        current_user_service=cus,
        deck_gateway=deck_gateway,
        deck_config_gateway=deck_config_gateway,
        card_gateway=card_gateway,
        user_gateway=user_gateway,
        access_service=access_service,
        deck_service=deck_service,
        deck_config_service=deck_config_service,
        card_service=card_service,
    )


async def test_copies_deck_with_cards(
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_card_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_service: Mock,
    fake_deck_config_service: Mock,
    fake_card_service: Mock,
) -> None:
    # Arrange
    new_config = create_deck_config()
    new_deck = create_deck()
    fake_deck_gateway.read_by_id.return_value = create_deck(is_public=True)
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()
    fake_deck_config_service.copy_config.return_value = new_config
    fake_deck_service.copy_deck.return_value = new_deck
    fake_card_gateway.read_all_by_deck.return_value = [create_card(), create_card()]
    fake_card_service.copy_card.return_value = create_card()
    handler = _handler(
        fake_transaction_manager,
        fake_current_user_service,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_card_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_deck_service,
        fake_deck_config_service,
        fake_card_service,
    )

    # Act
    result = await handler(CopyDeckCommand(source_deck_id=uuid4()))

    # Assert
    assert isinstance(result, CopyDeckView)
    assert result.deck_id == new_deck.id
    assert result.deck_config_id == new_config.id
    fake_deck_config_gateway.add.assert_awaited_once_with(new_config)
    fake_deck_gateway.add.assert_awaited_once_with(new_deck)
    assert fake_card_gateway.add.await_count == 2
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_source_deck_not_found(
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_card_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_service: Mock,
    fake_deck_config_service: Mock,
    fake_card_service: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_transaction_manager,
        fake_current_user_service,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_card_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_deck_service,
        fake_deck_config_service,
        fake_card_service,
    )

    # Act & Assert
    with pytest.raises(DeckNotFoundError):
        await handler(CopyDeckCommand(source_deck_id=uuid4()))
