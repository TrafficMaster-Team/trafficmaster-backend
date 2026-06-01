from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.card_progress_entity import create_card_progress
from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.ports.card_progress.card_with_progress import CardWithProgress
from trafficmaster.application.common.views.card_progress.review_queue_item import ReviewQueueItemView, ReviewReason
from trafficmaster.application.queries.card_progress.read_review_queue import (
    ReadReviewQueueQuery,
    ReadReviewQueueQueryHandler,
)


async def test_builds_queue_from_learning_review_and_new(
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_clock: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()
    fake_card_progress_gateway.read_due_learning.return_value = [
        CardWithProgress(card=create_card(), progress=create_card_progress()),
    ]
    fake_card_progress_gateway.read_due_review.return_value = [
        CardWithProgress(card=create_card(), progress=create_card_progress()),
    ]
    fake_card_progress_gateway.read_new_cards.return_value = [
        CardWithProgress(card=create_card(), progress=None),
    ]
    handler = ReadReviewQueueQueryHandler(
        current_user_service=fake_current_user_service,
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
        access_service=fake_access_service,
        deck_config_gateway=fake_deck_config_gateway,
        card_progress_gateway=fake_card_progress_gateway,
        review_log_gateway=fake_review_log_gateway,
        clock=fake_clock,
    )

    # Act
    result = await handler(ReadReviewQueueQuery(deck_id=uuid4(), limit=10))

    # Assert
    assert len(result) == 3
    assert all(isinstance(item, ReviewQueueItemView) for item in result)
    reasons = [item.reason for item in result]
    assert reasons == [ReviewReason.LEARNING, ReviewReason.REVIEW, ReviewReason.NEW]
    # the NEW item had no progress
    assert result[-1].state is None


async def test_stops_when_limit_reached_by_learning(
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_config_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_clock: Mock,
) -> None:
    # Arrange: learning already fills the limit
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()
    fake_card_progress_gateway.read_due_learning.return_value = [
        CardWithProgress(card=create_card(), progress=create_card_progress()),
    ]
    handler = ReadReviewQueueQueryHandler(
        current_user_service=fake_current_user_service,
        deck_gateway=fake_deck_gateway,
        user_gateway=fake_user_gateway,
        access_service=fake_access_service,
        deck_config_gateway=fake_deck_config_gateway,
        card_progress_gateway=fake_card_progress_gateway,
        review_log_gateway=fake_review_log_gateway,
        clock=fake_clock,
    )

    # Act
    result = await handler(ReadReviewQueueQuery(deck_id=uuid4(), limit=1))

    # Assert
    assert len(result) == 1
    fake_card_progress_gateway.read_due_review.assert_not_called()
    fake_card_progress_gateway.read_new_cards.assert_not_called()
