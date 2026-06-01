from datetime import datetime
from unittest.mock import Mock

import pytest

from tests.unit.factories.card_progress_entity import create_card_progress
from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.values import (
    create_advanced_config,
    create_card_id,
    create_card_progress_id,
    create_ease_factor,
    create_interval,
    create_lapses_config,
    create_new_cards_config,
    create_review_log_id,
    create_user_id,
)
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.services.card_progress_service import CardProgressService
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


@pytest.fixture
def service(card_progress_id_generator: Mock, review_id_generator: Mock) -> CardProgressService:
    review_id_generator.return_value = create_review_log_id()
    return CardProgressService(
        card_progress_id_generator=card_progress_id_generator,
        review_id_generator=review_id_generator,
    )


# --- create_card_progress ---
def test_creates_new_card_progress(
    service: CardProgressService,
    card_progress_id_generator: Mock,
) -> None:
    # Arrange
    expected_id = create_card_progress_id()
    card_progress_id_generator.return_value = expected_id
    user_id = create_user_id()
    card_id = create_card_id()
    ease = create_ease_factor(2.5)

    # Act
    result = service.create_card_progress(user_id=user_id, card_id=card_id, default_ease_factor=ease)

    # Assert
    assert isinstance(result, CardProgress)
    assert result.id == expected_id
    assert result.user_id == user_id
    assert result.card_id == card_id
    assert result.ease_factor == ease
    assert result.interval == create_interval(1)
    assert result.repetitions == 0
    assert result.state == CardState.NEW
    assert result.next_review_at is None


# --- learning_process ---
def test_learning_again_resets_repetitions(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.NEW, repetitions=3)
    config = create_new_cards_config(learning_steps=[1, 10])

    # Act
    log = service.learning_process(progress=progress, rating=ReviewRating.AGAIN, config=config)

    # Assert
    assert progress.state == CardState.LEARNING
    assert progress.repetitions == 0
    assert isinstance(progress.next_review_at, datetime)
    assert log.card_state == CardState.NEW
    assert log.rating == ReviewRating.AGAIN


def test_learning_hard_keeps_learning_state(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.LEARNING, repetitions=1)
    config = create_new_cards_config(learning_steps=[1, 10])

    # Act
    service.learning_process(progress=progress, rating=ReviewRating.HARD, config=config)

    # Assert
    assert progress.state == CardState.LEARNING
    assert progress.repetitions == 1
    assert isinstance(progress.next_review_at, datetime)


def test_learning_good_advances_step(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.LEARNING, repetitions=0)
    config = create_new_cards_config(learning_steps=[1, 10])

    # Act
    service.learning_process(progress=progress, rating=ReviewRating.GOOD, config=config)

    # Assert
    assert progress.state == CardState.LEARNING
    assert progress.repetitions == 1


def test_learning_good_graduates_to_review(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.LEARNING, repetitions=1)
    config = create_new_cards_config(learning_steps=[1, 10], graduating_interval=1)

    # Act
    service.learning_process(progress=progress, rating=ReviewRating.GOOD, config=config)

    # Assert
    assert progress.state == CardState.REVIEW
    assert progress.interval == create_interval(1)
    assert progress.repetitions == 1


def test_learning_easy_graduates_to_review(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.NEW, repetitions=0)
    config = create_new_cards_config(learning_steps=[1, 10], easy_interval=4)

    # Act
    service.learning_process(progress=progress, rating=ReviewRating.EASY, config=config)

    # Assert
    assert progress.state == CardState.REVIEW
    assert progress.interval == create_interval(4)
    assert progress.repetitions == 1


# --- review_process ---
def test_review_good_grows_interval(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )
    config = create_advanced_config()

    # Act
    service.review_process(progress=progress, rating=ReviewRating.GOOD, config=config)

    # GOOD grows the interval to 25 days
    assert progress.interval == create_interval(25)
    assert progress.repetitions == 3
    assert progress.ease_factor.value == pytest.approx(2.5)
    assert progress.state == CardState.REVIEW


def test_review_hard_reduces_ease(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )
    config = create_advanced_config()

    # Act
    service.review_process(progress=progress, rating=ReviewRating.HARD, config=config)

    # HARD lowers ease to 2.35 and sets interval to 12 days
    assert progress.ease_factor.value == pytest.approx(2.35)
    assert progress.interval == create_interval(12)
    assert progress.repetitions == 3


def test_review_easy_boosts_ease_and_interval(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )
    config = create_advanced_config()

    # Act
    service.review_process(progress=progress, rating=ReviewRating.EASY, config=config)

    # EASY raises ease to 2.65 and sets interval to 34 days
    assert progress.ease_factor.value == pytest.approx(2.65)
    assert progress.interval == create_interval(34)
    assert progress.repetitions == 3


def test_review_again_moves_to_relearning(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )
    config = create_advanced_config()

    # Act
    service.review_process(progress=progress, rating=ReviewRating.AGAIN, config=config)

    # AGAIN lowers ease to 2.3 and resets interval to 1 day
    assert progress.state == CardState.RELEARNING
    assert progress.ease_factor.value == pytest.approx(2.3)
    assert progress.interval == create_interval(1)
    assert progress.repetitions == 0


def test_review_interval_capped_at_max(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )
    config = create_advanced_config(max_interval=20)

    # Act: GOOD would grow the interval beyond the configured cap
    service.review_process(progress=progress, rating=ReviewRating.GOOD, config=config)

    # Assert
    assert progress.interval == create_interval(20)


# --- relearning_process ---
def test_relearning_again_resets_repetitions(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.RELEARNING, interval=create_interval(5), repetitions=2)
    config = create_lapses_config(relearning_steps=[10])

    # Act
    service.relearning_process(progress=progress, rating=ReviewRating.AGAIN, config=config)

    # Assert
    assert progress.state == CardState.RELEARNING
    assert progress.repetitions == 0


def test_relearning_good_graduates_to_review(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.RELEARNING, interval=create_interval(5), repetitions=0)
    config = create_lapses_config(relearning_steps=[10], min_interval=1)

    # Act
    service.relearning_process(progress=progress, rating=ReviewRating.GOOD, config=config)

    # interval keeps the larger of the configured minimum and the current value
    assert progress.state == CardState.REVIEW
    assert progress.interval == create_interval(5)
    assert progress.repetitions == 1


def test_relearning_respects_min_interval(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.RELEARNING, interval=create_interval(2), repetitions=0)
    config = create_lapses_config(relearning_steps=[10], min_interval=7)

    # Act
    service.relearning_process(progress=progress, rating=ReviewRating.EASY, config=config)

    # interval is raised to the configured minimum
    assert progress.state == CardState.REVIEW
    assert progress.interval == create_interval(7)


# --- schedule (dispatch) ---
def test_schedule_routes_new_card_to_learning(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.NEW, repetitions=0)
    deck_config = create_deck_config(new_cards=create_new_cards_config(learning_steps=[1, 10]))

    # Act
    log = service.schedule(progress=progress, rating=ReviewRating.GOOD, deck=deck_config)

    # Assert
    assert isinstance(log, ReviewLog)
    assert progress.state == CardState.LEARNING
    assert progress.repetitions == 1


def test_schedule_routes_review_card_to_review(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )
    deck_config = create_deck_config(advanced=create_advanced_config())

    # Act
    service.schedule(progress=progress, rating=ReviewRating.GOOD, deck=deck_config)

    # Assert
    assert progress.state == CardState.REVIEW
    assert progress.interval == create_interval(25)


def test_schedule_routes_relearning_card_to_relearning(service: CardProgressService) -> None:
    # Arrange
    progress = create_card_progress(state=CardState.RELEARNING, interval=create_interval(5), repetitions=0)
    deck_config = create_deck_config(lapses=create_lapses_config(relearning_steps=[10]))

    # Act
    service.schedule(progress=progress, rating=ReviewRating.GOOD, deck=deck_config)

    # Assert
    assert progress.state == CardState.REVIEW


def test_review_log_carries_user_and_card_ids(
    service: CardProgressService,
    review_id_generator: Mock,
) -> None:
    # Arrange
    expected_log_id = create_review_log_id()
    review_id_generator.return_value = expected_log_id
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(10),
        repetitions=2,
    )

    # Act
    log = service.review_process(progress=progress, rating=ReviewRating.GOOD, config=create_advanced_config())

    # Assert
    assert log.id == expected_log_id
    assert log.user_id == progress.user_id
    assert log.card_id == progress.card_id
    assert log.card_state == CardState.REVIEW
