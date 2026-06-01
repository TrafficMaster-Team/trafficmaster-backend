from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_card_tag
from trafficmaster.application.commands.card.add_tag import AddTagCommand, AddTagCommandHandler
from trafficmaster.application.errors.card import CardNotFoundError


def _handler(
    card_gateway: Mock, tx: Mock, cus: Mock, acl: Mock, deck_gateway: Mock, user_gateway: Mock
) -> AddTagCommandHandler:
    return AddTagCommandHandler(
        card_gateway=card_gateway,
        transaction_manager=tx,
        current_user_service=cus,
        access_service=acl,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
    )


async def test_adds_tag_successfully(
    fake_card_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    card = create_card(tags=[])
    fake_card_gateway.read_by_id.return_value = card
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_card_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
        fake_deck_gateway,
        fake_user_gateway,
    )

    # Act
    await handler(AddTagCommand(card_id=uuid4(), tag="grammar"))

    # Assert
    assert create_card_tag("grammar") in card.tags
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_card_not_found(
    fake_card_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_card_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
        fake_deck_gateway,
        fake_user_gateway,
    )

    # Act & Assert
    with pytest.raises(CardNotFoundError):
        await handler(AddTagCommand(card_id=uuid4(), tag="grammar"))
    fake_transaction_manager.commit.assert_not_called()
