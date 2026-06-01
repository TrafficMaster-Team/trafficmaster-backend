from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.card_progress_entity import create_card_progress, create_review_log
from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_interval
from trafficmaster.application.commands.card_progress.review_card import (
    ReviewCardCommand,
    ReviewCardCommandHandler,
)
from trafficmaster.application.common.views.card_progress.review_card import ReviewCardView
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.deck import DeckConfigNotFoundError
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


def _handler(
    tx: Mock,
    card_gateway: Mock,
    cus: Mock,
    deck_gateway: Mock,
    deck_config_gateway: Mock,
    user_gateway: Mock,
    access_service: Mock,
    card_progress_service: Mock,
    card_progress_gateway: Mock,
    review_log_gateway: Mock,
) -> ReviewCardCommandHandler:
    return ReviewCardCommandHandler(
        transaction_manager=tx,
        card_gateway=card_gateway,
        current_user_service=cus,
        deck_gateway=deck_gateway,
        deck_config_gateway=deck_config_gateway,
        user_gateway=user_gateway,
        access_service=access_service,
        card_progress_service=card_progress_service,
        card_progress_gateway=card_progress_gateway,
        review_log_gateway=review_log_gateway,
    )


def _setup_happy_path(
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_deck_config_gateway: Mock,
) -> None:
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = create_deck_config()


async def test_reviews_existing_progress(
    fake_transaction_manager: Mock,
    fake_card_gateway: Mock,
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_card_progress_service: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
) -> None:
    # Arrange
    _setup_happy_path(fake_card_gateway, fake_deck_gateway, fake_user_gateway, fake_deck_config_gateway)
    progress = create_card_progress(state=CardState.REVIEW, interval=create_interval(15))
    review_log = create_review_log()
    fake_card_progress_gateway.read_by_user_and_card.return_value = progress
    fake_card_progress_service.schedule.return_value = review_log
    handler = _handler(
        fake_transaction_manager,
        fake_card_gateway,
        fake_current_user_service,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_card_progress_service,
        fake_card_progress_gateway,
        fake_review_log_gateway,
    )

    # Act
    result = await handler(ReviewCardCommand(card_id=uuid4(), rating=ReviewRating.GOOD))

    # Assert
    assert isinstance(result, ReviewCardView)
    assert result.card_progress_id == progress.id
    assert result.review_log_id == review_log.id
    assert result.interval == 15
    fake_card_progress_gateway.add.assert_not_called()
    fake_review_log_gateway.add.assert_awaited_once_with(review_log)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_creates_progress_when_missing(
    fake_transaction_manager: Mock,
    fake_card_gateway: Mock,
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_card_progress_service: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
) -> None:
    # Arrange
    _setup_happy_path(fake_card_gateway, fake_deck_gateway, fake_user_gateway, fake_deck_config_gateway)
    new_progress = create_card_progress(state=CardState.NEW)
    fake_card_progress_gateway.read_by_user_and_card.return_value = None
    fake_card_progress_service.create_card_progress.return_value = new_progress
    fake_card_progress_service.schedule.return_value = create_review_log()
    handler = _handler(
        fake_transaction_manager,
        fake_card_gateway,
        fake_current_user_service,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_card_progress_service,
        fake_card_progress_gateway,
        fake_review_log_gateway,
    )

    # Act
    await handler(ReviewCardCommand(card_id=uuid4(), rating=ReviewRating.AGAIN))

    # Assert
    fake_card_progress_service.create_card_progress.assert_called_once()
    fake_card_progress_gateway.add.assert_awaited_once_with(new_progress)
    fake_transaction_manager.commit.assert_awaited_once()


async def test_fails_when_card_not_found(
    fake_transaction_manager: Mock,
    fake_card_gateway: Mock,
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_card_progress_service: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_transaction_manager,
        fake_card_gateway,
        fake_current_user_service,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_card_progress_service,
        fake_card_progress_gateway,
        fake_review_log_gateway,
    )

    # Act & Assert
    with pytest.raises(CardNotFoundError):
        await handler(ReviewCardCommand(card_id=uuid4(), rating=ReviewRating.GOOD))


async def test_fails_when_deck_config_not_found(
    fake_transaction_manager: Mock,
    fake_card_gateway: Mock,
    fake_current_user_service: Mock,
    fake_deck_gateway: Mock,
    fake_deck_config_gateway: Mock,
    fake_user_gateway: Mock,
    fake_access_service: Mock,
    fake_card_progress_service: Mock,
    fake_card_progress_gateway: Mock,
    fake_review_log_gateway: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_config_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_transaction_manager,
        fake_card_gateway,
        fake_current_user_service,
        fake_deck_gateway,
        fake_deck_config_gateway,
        fake_user_gateway,
        fake_access_service,
        fake_card_progress_service,
        fake_card_progress_gateway,
        fake_review_log_gateway,
    )

    # Act & Assert
    with pytest.raises(DeckConfigNotFoundError):
        await handler(ReviewCardCommand(card_id=uuid4(), rating=ReviewRating.GOOD))
