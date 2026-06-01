from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.card_progress_entity import create_review_log
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.views.card_progress.review_log import ReviewLogView
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.queries.card_progress.read_review_log_by_card import (
    ReadReviewLogByCardQuery,
    ReadReviewLogByCardQueryHandler,
)


def _handler(
    cus: Mock,
    card_gateway: Mock,
    deck_gateway: Mock,
    user_gateway: Mock,
    review_log_gateway: Mock,
    access_service: Mock,
) -> ReadReviewLogByCardQueryHandler:
    return ReadReviewLogByCardQueryHandler(
        current_user_service=cus,
        card_gateway=card_gateway,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        review_log_gateway=review_log_gateway,
        access_service=access_service,
    )


async def test_reads_review_logs_by_card(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_review_log_gateway.read_by_card.return_value = [create_review_log(), create_review_log()]
    handler = _handler(
        fake_current_user_service,
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_review_log_gateway,
        fake_access_service,
    )

    # Act
    result = await handler(ReadReviewLogByCardQuery(card_id=uuid4(), limit=10, offset=0))

    # Assert
    assert len(result) == 2
    assert all(isinstance(view, ReviewLogView) for view in result)


async def test_fails_when_card_not_found(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_review_log_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_review_log_gateway,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(CardNotFoundError):
        await handler(ReadReviewLogByCardQuery(card_id=uuid4()))
