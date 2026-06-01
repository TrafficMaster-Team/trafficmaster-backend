from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck.change_title import ChangeTitleCommand, ChangeTitleCommandHandler


async def test_changes_title_successfully(
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
    handler = ChangeTitleCommandHandler(
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
    )

    # Act
    await handler(ChangeTitleCommand(deck_id=uuid4(), title="New Title"))

    # Assert
    assert str(deck.title) == "New Title"
    fake_transaction_manager.commit.assert_awaited_once()
