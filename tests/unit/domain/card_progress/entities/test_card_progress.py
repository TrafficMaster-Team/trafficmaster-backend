from datetime import UTC, datetime

import pytest

from tests.unit.factories.card_progress_entity import create_card_progress
from tests.unit.factories.values import (
    create_card_id,
    create_card_progress_id,
    create_ease_factor,
    create_interval,
    create_user_id,
)
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.common.errors import DomainError


def test_creates_card_progress_with_given_values() -> None:
    # Arrange
    progress_id = create_card_progress_id()
    user_id = create_user_id()
    card_id = create_card_id()
    ease = create_ease_factor(2.5)
    interval = create_interval(3)
    next_review = datetime(2026, 6, 1, tzinfo=UTC)

    # Act
    sut = create_card_progress(
        progress_id=progress_id,
        user_id=user_id,
        card_id=card_id,
        ease_factor=ease,
        interval=interval,
        repetitions=2,
        state=CardState.REVIEW,
        next_review_at=next_review,
    )

    # Assert
    assert sut.id == progress_id
    assert sut.user_id == user_id
    assert sut.card_id == card_id
    assert sut.ease_factor == ease
    assert sut.interval == interval
    assert sut.repetitions == 2
    assert sut.state == CardState.REVIEW
    assert sut.next_review_at == next_review


def test_new_card_progress_has_no_next_review() -> None:
    sut = create_card_progress()

    assert sut.state == CardState.NEW
    assert sut.next_review_at is None


def test_card_progress_id_cannot_be_changed() -> None:
    sut = create_card_progress()

    with pytest.raises(DomainError):
        sut.id = create_card_progress_id()


def test_card_progress_is_mutable_except_id() -> None:
    sut = create_card_progress()

    sut.state = CardState.LEARNING
    sut.repetitions = 5
    sut.interval = create_interval(10)

    assert sut.state == CardState.LEARNING
    assert sut.repetitions == 5
    assert sut.interval == create_interval(10)


def test_progresses_with_same_id_are_equal() -> None:
    same_id = create_card_progress_id()
    p1 = create_card_progress(progress_id=same_id, repetitions=1)
    p2 = create_card_progress(progress_id=same_id, repetitions=99)

    assert p1 == p2
    assert hash(p1) == hash(p2)


def test_progresses_with_different_id_are_not_equal() -> None:
    assert create_card_progress(progress_id=create_card_progress_id()) != create_card_progress(
        progress_id=create_card_progress_id(),
    )
