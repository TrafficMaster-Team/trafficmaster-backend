from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import (
    create_advanced_config,
    create_daily_limits,
    create_lapses_config,
    create_new_cards_config,
)
from trafficmaster.application.commands.deck_config.create_deck_config import (
    CreateDeckConfigCommand,
    CreateDeckConfigCommandHandler,
)
from trafficmaster.application.common.views.deck_config.create_deck_config import CreateDeckConfigView
from trafficmaster.application.errors.user import NoPermissionToManageUserError


def _command() -> CreateDeckConfigCommand:
    return CreateDeckConfigCommand(
        owner_id=uuid4(),
        name="Default",
        daily_limits=create_daily_limits(),
        new_cards=create_new_cards_config(),
        lapses=create_lapses_config(),
        advanced=create_advanced_config(),
    )


def _handler(
    cus: Mock, user_gateway: Mock, acl: Mock, tx: Mock, gw: Mock, service: Mock
) -> CreateDeckConfigCommandHandler:
    return CreateDeckConfigCommandHandler(
        current_user_service=cus,
        user_gateway=user_gateway,
        access_service=acl,
        transaction_manager=tx,
        deck_config_gateway=gw,
        deck_config_service=service,
    )


async def test_creates_deck_config_successfully(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_config_gateway: Mock,
    fake_deck_config_service: Mock,
) -> None:
    # Arrange
    created = create_deck_config()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_service.create_config.return_value = created
    handler = _handler(
        fake_current_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_config_gateway,
        fake_deck_config_service,
    )

    # Act
    result = await handler(_command())

    # Assert
    assert isinstance(result, CreateDeckConfigView)
    assert result.id == created.id
    fake_deck_config_gateway.add.assert_awaited_once_with(created)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_no_permission(
    fake_current_user_service: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_transaction_manager: Mock,
    fake_deck_config_gateway: Mock,
    fake_deck_config_service: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service,
        fake_user_gateway,
        fake_access_service,
        fake_transaction_manager,
        fake_deck_config_gateway,
        fake_deck_config_service,
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(_command())
    fake_deck_config_gateway.add.assert_not_called()
