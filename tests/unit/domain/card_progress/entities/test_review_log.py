from datetime import UTC, datetime

import pytest

from tests.unit.factories.card_progress_entity import create_review_log
from tests.unit.factories.values import (
    create_card_id,
    create_review_log_id,
    create_user_id,
)
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.common.errors import DomainError


def test_creates_review_log_with_given_values() -> None:
    # Arrange
    log_id = create_review_log_id()
    user_id = create_user_id()
    card_id = create_card_id()
    reviewed_at = datetime(2026, 6, 1, tzinfo=UTC)

    # Act
    sut = create_review_log(
        review_log_id=log_id,
        user_id=user_id,
        card_id=card_id,
        rating=ReviewRating.EASY,
        card_state=CardState.REVIEW,
        reviewed_at=reviewed_at,
    )

    # Assert
    assert sut.id == log_id
    assert sut.user_id == user_id
    assert sut.card_id == card_id
    assert sut.rating == ReviewRating.EASY
    assert sut.card_state == CardState.REVIEW
    assert sut.reviewed_at == reviewed_at


def test_review_log_id_cannot_be_changed() -> None:
    sut = create_review_log()

    with pytest.raises(DomainError):
        sut.id = create_review_log_id()


def test_review_logs_with_same_id_are_equal() -> None:
    same_id = create_review_log_id()
    log1 = create_review_log(review_log_id=same_id, rating=ReviewRating.AGAIN)
    log2 = create_review_log(review_log_id=same_id, rating=ReviewRating.GOOD)

    assert log1 == log2
    assert hash(log1) == hash(log2)
