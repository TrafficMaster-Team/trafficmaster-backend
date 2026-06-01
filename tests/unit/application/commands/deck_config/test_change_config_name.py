from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.commands.deck_config.change_config_name import (
    ChangeConfigNameCommand,
    ChangeConfigNameCommandHandler,
)
from trafficmaster.application.errors.deck import DeckConfigNotFoundError


def _handler(gw: Mock, user_gateway: Mock, tx: Mock, cus: Mock, acl: Mock) -> ChangeConfigNameCommandHandler:
    return ChangeConfigNameCommandHandler(
        deck_config_gateway=gw,
        user_gateway=user_gateway,
        transaction_manager=tx,
        current_user_service=cus,
        access_service=acl,
    )


async def test_changes_name_successfully(
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    config = create_deck_config()
    fake_deck_config_gateway.read_by_id.return_value = config
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act
    await handler(ChangeConfigNameCommand(deck_config_id=uuid4(), name="Renamed"))

    # Assert
    assert str(config.name) == "Renamed"
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_config_not_found(
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_deck_config_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_transaction_manager,
        fake_current_user_service,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(DeckConfigNotFoundError):
        await handler(ChangeConfigNameCommand(deck_config_id=uuid4(), name="Renamed"))
