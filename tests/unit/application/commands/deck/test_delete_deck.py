from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck.delete_deck import DeleteDeckCommand, DeleteDeckCommandHandler
from trafficmaster.application.errors.deck import DeckNotFoundError


def _handler(deck_gateway: Mock, user_gateway: Mock, tx: Mock, cus: Mock, acl: Mock) -> DeleteDeckCommandHandler:
    return DeleteDeckCommandHandler(
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        transaction_manager=tx,
        current_user_service=cus,
        access_service=acl,
    )


async def test_deletes_deck_successfully(
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    deck = create_deck()
    fake_deck_gateway.read_by_id.return_value = deck
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_deck_gateway, fake_user_gateway, fake_transaction_manager, fake_current_user_service, fake_access_service
    )

    # Act
    await handler(DeleteDeckCommand(deck_id=uuid4()))

    # Assert
    fake_deck_gateway.delete_by_id.assert_awaited_once_with(deck.id)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_deck_not_found(
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_deck_gateway, fake_user_gateway, fake_transaction_manager, fake_current_user_service, fake_access_service
    )

    # Act & Assert
    with pytest.raises(DeckNotFoundError):
        await handler(DeleteDeckCommand(deck_id=uuid4()))
    fake_deck_gateway.delete_by_id.assert_not_called()
