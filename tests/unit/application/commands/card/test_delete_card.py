from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.card.delete_card import (
    DeleteCardCommand,
    DeleteCardCommandHandler,
)
from trafficmaster.application.errors.deck import DeckNotFoundError


def _handler(
    card_gateway: Mock, deck_gateway: Mock, user_gateway: Mock, tx: Mock, cus: Mock, acl: Mock
) -> DeleteCardCommandHandler:
    return DeleteCardCommandHandler(
        card_gateway=card_gateway,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        transaction_manager=tx,
        current_user_service=cus,
        access_service=acl,
    )


async def test_deletes_card_successfully(
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    card = create_card()
    fake_card_gateway.read_by_id.return_value = card
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act
    await handler(DeleteCardCommand(card_id=uuid4()))

    # Assert
    fake_card_gateway.delete_by_id.assert_awaited_once_with(card.id)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_deck_not_found(
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(DeckNotFoundError):
        await handler(DeleteCardCommand(card_id=uuid4()))
    fake_card_gateway.delete_by_id.assert_not_called()
