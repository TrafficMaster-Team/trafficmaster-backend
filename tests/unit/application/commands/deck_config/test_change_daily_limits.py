from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_daily_limits
from trafficmaster.application.commands.deck_config.change_daily_limits import (
    ChangeDailyLimitsCommand,
    ChangeDailyLimitsCommandHandler,
)


async def test_changes_daily_limits_successfully(
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_transaction_manager: Mock,
    fake_current_user_service: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    config = create_deck_config()
    new_limits = create_daily_limits(new_cards_per_day=5, max_reviews_per_day=50)
    fake_deck_config_gateway.read_by_id.return_value = config
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = ChangeDailyLimitsCommandHandler(
        deck_config_gateway=fake_deck_config_gateway,
        user_gateway=fake_user_gateway,
        transaction_manager=fake_transaction_manager,
        current_user_service=fake_current_user_service,
        access_service=fake_access_service,
    )

    # Act
    await handler(ChangeDailyLimitsCommand(deck_config_id=uuid4(), daily_limits=new_limits))

    # Assert
    assert config.daily_limits == new_limits
    fake_transaction_manager.commit.assert_awaited_once()
