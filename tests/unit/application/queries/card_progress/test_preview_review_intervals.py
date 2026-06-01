from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.card_progress_entity import create_card_progress
from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.views.card_progress.preview_review_intervals import PreviewReviewIntervalsView
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.queries.card_progress.preview_review_intervals import (
    PreviewReviewIntervalsQuery,
    PreviewReviewIntervalsQueryHandler,
)
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


def _handler(
    cus: Mock,
    card_gateway: Mock,
    deck_gateway: Mock,
    deck_config_gateway: Mock,
    user_gateway: Mock,
    card_progress_gateway: Mock,
    access_service: Mock,
    card_progress_service: Mock,
) -> PreviewReviewIntervalsQueryHandler:
    return PreviewReviewIntervalsQueryHandler(
        current_user_service=cus,
        card_gateway=card_gateway,
        deck_gateway=deck_gateway,
        deck_config_gateway=deck_config_gateway,
        user_gateway=user_gateway,
        card_progress_gateway=card_progress_gateway,
        access_service=access_service,
        card_progress_service=card_progress_service,
    )


async def test_previews_intervals_for_all_ratings(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_access_service: Mock,
    fake_card_progress_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()
    fake_card_progress_gateway.read_by_user_and_card.return_value = create_card_progress(state=CardState.REVIEW)
    handler = _handler(
        fake_current_user_service,
        fake_card_gateway,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_card_progress_gateway,
        fake_access_service,
        fake_card_progress_service,
    )

    # Act
    result = await handler(PreviewReviewIntervalsQuery(card_id=uuid4()))

    # Assert: one preview item per rating
    assert isinstance(result, PreviewReviewIntervalsView)
    assert len(result.items) == 4
    assert {item.rating for item in result.items} == {
        ReviewRating.AGAIN,
        ReviewRating.HARD,
        ReviewRating.GOOD,
        ReviewRating.EASY,
    }
    assert fake_card_progress_service.schedule.call_count == 4


async def test_fails_when_card_not_found(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_access_service: Mock,
    fake_card_progress_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_card_gateway,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_card_progress_gateway,
        fake_access_service,
        fake_card_progress_service,
    )

    # Act & Assert
    with pytest.raises(CardNotFoundError):
        await handler(PreviewReviewIntervalsQuery(card_id=uuid4()))
