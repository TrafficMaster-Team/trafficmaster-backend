from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck.change_description import (
    ChangeDescriptionCommand,
    ChangeDescriptionCommandHandler,
)


@pytest.mark.parametrize("description", [pytest.param("new desc", id="set"), pytest.param(None, id="cleared")])
async def test_changes_description_successfully(
    description: str | None,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    deck = create_deck(description="old")
    fake_deck_gateway.read_by_id.return_value = deck
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = ChangeDescriptionCommandHandler(
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
    )

    # Act
    await handler(ChangeDescriptionCommand(deck_id=uuid4(), description=description))

    # Assert
    assert deck.description == description
    fake_transaction_manager.commit.assert_awaited_once()
