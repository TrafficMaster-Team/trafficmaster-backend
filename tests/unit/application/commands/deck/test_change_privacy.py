from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck.change_privacy import (
    ChangePrivacyCommand,
    ChangePrivacyCommandHandler,
)


@pytest.mark.parametrize("is_public", [True, False])
async def test_changes_privacy_successfully(
    is_public: bool,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    deck = create_deck(is_public=not is_public)
    fake_deck_gateway.read_by_id.return_value = deck
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = ChangePrivacyCommandHandler(
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
    )

    # Act
    await handler(ChangePrivacyCommand(deck_id=uuid4(), is_public=is_public))

    # Assert
    assert deck.is_public is is_public
    fake_transaction_manager.commit.assert_awaited_once()
