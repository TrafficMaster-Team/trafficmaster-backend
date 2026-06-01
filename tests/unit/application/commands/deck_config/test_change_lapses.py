from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_lapses_config
from trafficmaster.application.commands.deck_config.change_lapses import (
    ChangeLapsesCommand,
    ChangeLapsesCommandHandler,
)


async def test_changes_lapses_successfully(
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    config = create_deck_config()
    new_lapses = create_lapses_config(relearning_steps=[20])
    fake_deck_config_gateway.read_by_id.return_value = config
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = ChangeLapsesCommandHandler(
        deck_config_gateway=fake_deck_config_gateway,
        user_gateway=fake_user_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
    )

    # Act
    await handler(ChangeLapsesCommand(deck_config_id=uuid4(), lapses=new_lapses))

    # Assert
    assert config.lapses == new_lapses
    fake_transaction_manager.commit.assert_awaited_once()
