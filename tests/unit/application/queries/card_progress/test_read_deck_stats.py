from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.views.card_progress.read_deck_stats import ReadDeckStatsView
from trafficmaster.application.errors.deck import DeckConfigNotFoundError
from trafficmaster.application.queries.card_progress.read_deck_stats import (
    ReadDeckStatsQuery,
    ReadDeckStatsQueryHandler,
)
from trafficmaster.domain.card_progress.values.card_state import CardState


def _handler(
    cus: Mock,
    deck_gateway: Mock,
    user_gateway: Mock,
    access_service: Mock,
    deck_config_gateway: Mock,
    card_gateway: Mock,
    card_progress_gateway: Mock,
    review_log_gateway: Mock,
    clock: Mock,
) -> ReadDeckStatsQueryHandler:
    return ReadDeckStatsQueryHandler(
        current_user_service=cus,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        access_service=access_service,
        deck_config_gateway=deck_config_gateway,
        card_gateway=card_gateway,
        card_progress_gateway=card_progress_gateway,
        review_log_gateway=review_log_gateway,
        clock=clock,
    )


async def test_reads_deck_stats(
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_card_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_clock: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()
    fake_card_gateway.count_by_deck.return_value = 50
    fake_card_progress_gateway.count_by_state.return_value = {
        CardState.LEARNING: 5,
        CardState.RELEARNING: 2,
        CardState.REVIEW: 10,
    }
    fake_card_progress_gateway.count_due_learning.return_value = 4
    fake_card_progress_gateway.count_due_review.return_value = 6
    fake_review_log_gateway.count_new_done.return_value = 3
    fake_review_log_gateway.count_reviews_done.return_value = 9
    handler = _handler(
        fake_current_user_service,
        fake_deck_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_deck_config_gateway,
        fake_card_gateway,
        fake_card_progress_gateway,
        fake_review_log_gateway,
        fake_clock,
    )

    # Act
    result = await handler(ReadDeckStatsQuery(deck_id=uuid4()))

    # Assert
    assert isinstance(result, ReadDeckStatsView)
    assert result.total_cards == 50
    assert result.learning_count == 7
    assert result.review_count == 10
    assert result.new_count == 33
    assert result.new_done_today == 3
    # default new_cards_per_day=20 -> quota left 17 -> available min(33, 17)
    assert result.new_available == 17


async def test_fails_when_deck_config_missing(
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_card_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_clock: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_deck_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_deck_config_gateway,
        fake_card_gateway,
        fake_card_progress_gateway,
        fake_review_log_gateway,
        fake_clock,
    )

    # Act & Assert
    with pytest.raises(DeckConfigNotFoundError):
        await handler(ReadDeckStatsQuery(deck_id=uuid4()))
