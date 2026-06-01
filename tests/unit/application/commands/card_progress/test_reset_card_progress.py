from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.card_progress_entity import create_card_progress
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.card_progress.reset_card_progress import (
    ResetCardProgressCommand,
    ResetCardProgressCommandHandler,
)
from trafficmaster.application.errors.card_progress import CardProgressNotFoundError


def _handler(
    tx: Mock,
    card_gateway: Mock,
    deck_gateway: Mock,
    user_gateway: Mock,
    card_progress_gateway: Mock,
    cus: Mock,
    access_service: Mock,
) -> ResetCardProgressCommandHandler:
    return ResetCardProgressCommandHandler(
        transaction_manager=tx,
        card_gateway=card_gateway,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        card_progress_gateway=card_progress_gateway,
        current_user_service=cus,
        access_service=access_service,
    )


async def test_resets_progress_successfully(
    fake_transaction_manager: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    progress = create_card_progress()
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_card_progress_gateway.read_by_user_and_card.return_value = progress
    handler = _handler(
        fake_transaction_manager,
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_card_progress_gateway,
        fake_current_user_service,
        fake_access_service,
    )

    # Act
    await handler(ResetCardProgressCommand(card_id=uuid4()))

    # Assert
    fake_card_progress_gateway.delete_by_id.assert_awaited_once_with(progress.id)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_progress_not_found(
    fake_transaction_manager: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_card_progress_gateway.read_by_user_and_card.return_value = None
    handler = _handler(
        fake_transaction_manager,
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_card_progress_gateway,
        fake_current_user_service,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(CardProgressNotFoundError):
        await handler(ResetCardProgressCommand(card_id=uuid4()))
    fake_card_progress_gateway.delete_by_id.assert_not_called()
