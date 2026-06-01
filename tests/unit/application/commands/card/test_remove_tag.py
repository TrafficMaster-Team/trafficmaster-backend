from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_card_tag
from trafficmaster.application.commands.card.remove_tag import RemoveTagCommand, RemoveTagCommandHandler


async def test_removes_tag_successfully(
    fake_card_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    card = create_card(tags=[create_card_tag("grammar")])
    fake_card_gateway.read_by_id.return_value = card
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = RemoveTagCommandHandler(
        card_gateway=fake_card_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
    )

    # Act
    await handler(RemoveTagCommand(card_id=uuid4(), tag="grammar"))

    # Assert
    assert create_card_tag("grammar") not in card.tags
    fake_transaction_manager.commit.assert_awaited_once()
