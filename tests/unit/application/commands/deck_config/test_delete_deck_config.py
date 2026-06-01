from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck_config.delete_deck_config import (
    DeleteDeckConfigCommand,
    DeleteDeckConfigCommandHandler,
)
from trafficmaster.application.errors.deck import DeckConfigInUseError, DeckConfigNotFoundError


def _handler(
    gw: Mock, deck_gateway: Mock, user_gateway: Mock, tx: Mock, cus: Mock, acl: Mock
) -> DeleteDeckConfigCommandHandler:
    return DeleteDeckConfigCommandHandler(
        deck_config_gateway=gw,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        transaction_manager=tx,
        current_user_service=cus,
        access_service=acl,
    )


async def test_deletes_deck_config_successfully(
    fake_deck_config_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    config = create_deck_config()
    fake_deck_config_gateway.read_by_id.return_value = config
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_gateway.exists_with_deck_config_id.return_value = False
    handler = _handler(
        fake_deck_config_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act
    await handler(DeleteDeckConfigCommand(deck_config_id=uuid4()))

    # Assert
    fake_deck_config_gateway.delete_by_id.assert_awaited_once_with(config.id)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_config_not_found(
    fake_deck_config_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_deck_config_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_deck_config_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(DeckConfigNotFoundError):
        await handler(DeleteDeckConfigCommand(deck_config_id=uuid4()))


async def test_fails_when_config_in_use(
    fake_deck_config_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_gateway.exists_with_deck_config_id.return_value = True
    handler = _handler(
        fake_deck_config_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(DeckConfigInUseError):
        await handler(DeleteDeckConfigCommand(deck_config_id=uuid4()))
    fake_deck_config_gateway.delete_by_id.assert_not_called()
