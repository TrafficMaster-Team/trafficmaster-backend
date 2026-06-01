from unittest.mock import Mock, create_autospec

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.views.user.aggregate_stats import UserAggregateStatsView
from trafficmaster.application.queries.user.read_aggregate_stats import ReadUserAggregateStatsQueryHandler
from trafficmaster.domain.card_progress.values.card_state import CardState


async def test_aggregates_user_stats(
    fake_current_user_service: Mock,
    fake_clock: Mock,
) -> None:
    # Arrange
    fake_current_user_service.get_current_user.return_value = create_user()

    deck_gateway = create_autospec(DeckGateway)
    deck_gateway.count_by_user.return_value = 3

    card_gateway = create_autospec(CardGateway)
    card_gateway.count_by_user.return_value = 50

    card_progress_gateway = create_autospec(CardProgressGateway)
    card_progress_gateway.count_by_state.return_value = {
        CardState.LEARNING: 5,
        CardState.RELEARNING: 2,
        CardState.REVIEW: 10,
    }
    card_progress_gateway.count_due_learning.return_value = 4
    card_progress_gateway.count_due_review.return_value = 6

    review_log_gateway = create_autospec(ReviewLogGateway)
    review_log_gateway.count_new_done.return_value = 8
    review_log_gateway.count_reviews_done.return_value = 9

    handler = ReadUserAggregateStatsQueryHandler(
        current_user_service=fake_current_user_service,
        deck_gateway=deck_gateway,
        card_gateway=card_gateway,
        card_progress_gateway=card_progress_gateway,
        review_log_gateway=review_log_gateway,
        clock=fake_clock,
    )

    # Act
    result = await handler()

    # Assert
    assert isinstance(result, UserAggregateStatsView)
    assert result.total_decks == 3
    assert result.total_cards == 50
    assert result.learning_count == 7  # LEARNING + RELEARNING
    assert result.review_count == 10
    assert result.new_count == 33  # 50 - 7 - 10
    assert result.due_learning == 4
    assert result.due_review == 6
    assert result.new_done_today == 8
    assert result.reviews_done_today == 9


async def test_new_count_never_negative(
    fake_current_user_service: Mock,
    fake_clock: Mock,
) -> None:
    # Arrange: more learning/review than total cards
    fake_current_user_service.get_current_user.return_value = create_user()

    deck_gateway = create_autospec(DeckGateway)
    deck_gateway.count_by_user.return_value = 1

    card_gateway = create_autospec(CardGateway)
    card_gateway.count_by_user.return_value = 5

    card_progress_gateway = create_autospec(CardProgressGateway)
    card_progress_gateway.count_by_state.return_value = {CardState.REVIEW: 10}
    card_progress_gateway.count_due_learning.return_value = 0
    card_progress_gateway.count_due_review.return_value = 0

    review_log_gateway = create_autospec(ReviewLogGateway)
    review_log_gateway.count_new_done.return_value = 0
    review_log_gateway.count_reviews_done.return_value = 0

    handler = ReadUserAggregateStatsQueryHandler(
        current_user_service=fake_current_user_service,
        deck_gateway=deck_gateway,
        card_gateway=card_gateway,
        card_progress_gateway=card_progress_gateway,
        review_log_gateway=review_log_gateway,
        clock=fake_clock,
    )

    # Act
    result = await handler()

    # Assert
    assert result.new_count == 0
