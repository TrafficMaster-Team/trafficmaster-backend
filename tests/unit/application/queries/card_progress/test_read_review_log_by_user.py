from unittest.mock import Mock
from uuid import uuid4

from tests.unit.factories.card_progress_entity import create_review_log
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.views.card_progress.review_log import ReviewLogView
from trafficmaster.application.queries.card_progress.read_review_log_by_user import (
    ReadReviewLogByUserQuery,
    ReadReviewLogByUserQueryHandler,
)


def _handler(
    cus: Mock,
    deck_gateway: Mock,
    user_gateway: Mock,
    review_log_gateway: Mock,
    access_service: Mock,
) -> ReadReviewLogByUserQueryHandler:
    return ReadReviewLogByUserQueryHandler(
        current_user_service=cus,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        review_log_gateway=review_log_gateway,
        access_service=access_service,
    )


async def test_reads_logs_across_all_decks(
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange: no deck_id -> skips deck lookup
    fake_review_log_gateway.read_by_user.return_value = [create_review_log()]
    handler = _handler(
        fake_current_user_service, fake_deck_gateway, fake_user_gateway, fake_review_log_gateway, fake_access_service
    )

    # Act
    result = await handler(ReadReviewLogByUserQuery())

    # Assert
    assert len(result) == 1
    assert isinstance(result[0], ReviewLogView)
    fake_deck_gateway.read_by_id.assert_not_called()


async def test_reads_logs_filtered_by_deck(
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange: deck_id provided -> validates deck ownership
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_review_log_gateway.read_by_user.return_value = [create_review_log(), create_review_log()]
    handler = _handler(
        fake_current_user_service, fake_deck_gateway, fake_user_gateway, fake_review_log_gateway, fake_access_service
    )

    # Act
    result = await handler(ReadReviewLogByUserQuery(deck_id=uuid4(), limit=5, offset=0))

    # Assert
    assert len(result) == 2
    fake_deck_gateway.read_by_id.assert_awaited_once()
