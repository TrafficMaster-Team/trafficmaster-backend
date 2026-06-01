from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.card.change_deck import (
    ChangeDeckCommand,
    ChangeDeckCommandHandler,
)


async def test_changes_deck_successfully(
    fake_card_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    card = create_card()
    new_deck_id = uuid4()
    fake_card_gateway.read_by_id.return_value = card
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = ChangeDeckCommandHandler(
        card_gateway=fake_card_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
    )

    # Act
    await handler(ChangeDeckCommand(card_id=uuid4(), deck_id=new_deck_id))

    # Assert
    assert card.deck_id == new_deck_id
    fake_transaction_manager.commit.assert_awaited_once()
