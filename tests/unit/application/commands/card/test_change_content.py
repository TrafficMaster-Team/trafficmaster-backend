from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_answer_option
from trafficmaster.application.commands.card.change_content import (
    ChangeCardContentCommand,
    ChangeCardContentCommandHandler,
)
from trafficmaster.application.commands.card.create_card import AnswerOptionData


async def test_changes_card_content_successfully(
    fake_card_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_service: Mock,
) -> None:
    # Arrange
    card = create_card()
    fake_card_gateway.read_by_id.return_value = card
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    updated_option = create_answer_option(text="Updated answer", rationale="Correct")
    fake_card_service.create_answer_option.return_value = updated_option
    handler = ChangeCardContentCommandHandler(
        card_gateway=fake_card_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
        card_service=fake_card_service,
    )

    # Act
    await handler(
        ChangeCardContentCommand(
            card_id=uuid4(),
            answer_options=[AnswerOptionData(text="Updated answer", is_correct=True, rationale="Correct")],
            hint="Updated hint",
        )
    )

    # Assert
    assert card.answer_options[0].text == "Updated answer"
    assert str(card.hint) == "Updated hint"
    fake_transaction_manager.commit.assert_awaited_once()
