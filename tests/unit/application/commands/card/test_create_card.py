from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.card.create_card import (
    CreateCardCommand,
    CreateCardCommandHandler,
)
from trafficmaster.application.common.views.card.create_card import CreateCardView
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import (
    NoPermissionToManageUserError,
    UserNotFoundByIdError,
)


def _handler(
    cus: Mock,
    card_service: Mock,
    user_gateway: Mock,
    access_service: Mock,
    tx: Mock,
    deck_gateway: Mock,
    card_gateway: Mock,
) -> CreateCardCommandHandler:
    return CreateCardCommandHandler(
        current_user_service=cus,
        card_service=card_service,
        user_gateway=user_gateway,
        access_service=access_service,
        transaction_manager=tx,
        deck_gateway=deck_gateway,
        card_gateway=card_gateway,
    )


def _command() -> CreateCardCommand:
    return CreateCardCommand(deck_id=uuid4(), question="Q?", answer="A", tags=["tag"])


async def test_creates_card_successfully(
    fake_current_user_service: Mock,
    fake_card_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_card_gateway: Mock,
) -> None:
    # Arrange
    created = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_card_service.create_card.return_value = created
    handler = _handler(
        fake_current_user_service,
        fake_card_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_card_gateway,
    )

    # Act
    result = await handler(_command())

    # Assert
    assert isinstance(result, CreateCardView)
    assert result.id == created.id
    fake_card_gateway.add.assert_awaited_once_with(created)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_deck_not_found(
    fake_current_user_service: Mock,
    fake_card_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_card_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_card_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_card_gateway,
    )

    # Act & Assert
    with pytest.raises(DeckNotFoundError):
        await handler(_command())
    fake_card_gateway.add.assert_not_called()


async def test_fails_when_owner_not_found(
    fake_current_user_service: Mock,
    fake_card_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_card_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_card_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_card_gateway,
    )

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(_command())


async def test_fails_when_no_permission(
    fake_current_user_service: Mock,
    fake_card_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_gateway: Mock,
    fake_card_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service,
        fake_card_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_gateway,
        fake_card_gateway,
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(_command())
    fake_card_gateway.add.assert_not_called()
