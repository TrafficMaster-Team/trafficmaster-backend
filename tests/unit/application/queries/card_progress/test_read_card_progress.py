from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.card_progress_entity import create_card_progress
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_ease_factor, create_interval
from trafficmaster.application.common.views.card_progress.read_card_progress import ReadCardProgressView
from trafficmaster.application.errors.card_progress import CardProgressNotFoundError
from trafficmaster.application.queries.card_progress.read_card_progress import (
    ReadCardProgressQuery,
    ReadCardProgressQueryHandler,
)
from trafficmaster.domain.card_progress.values.card_state import CardState


def _handler(
    cus: Mock,
    card_gateway: Mock,
    deck_gateway: Mock,
    user_gateway: Mock,
    card_progress_gateway: Mock,
    access_service: Mock,
) -> ReadCardProgressQueryHandler:
    return ReadCardProgressQueryHandler(
        current_user_service=cus,
        card_gateway=card_gateway,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
        card_progress_gateway=card_progress_gateway,
        access_service=access_service,
    )


async def test_reads_card_progress_successfully(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    progress = create_card_progress(
        state=CardState.REVIEW,
        ease_factor=create_ease_factor(2.5),
        interval=create_interval(12),
        repetitions=3,
    )
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_card_progress_gateway.read_by_user_and_card.return_value = progress
    handler = _handler(
        fake_current_user_service,
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_card_progress_gateway,
        fake_access_service,
    )

    # Act
    result = await handler(ReadCardProgressQuery(card_id=uuid4()))

    # Assert
    assert isinstance(result, ReadCardProgressView)
    assert result.id == progress.id
    assert result.state == CardState.REVIEW
    assert result.ease_factor == 2.5
    assert result.interval == 12
    assert result.repetitions == 3


async def test_fails_when_progress_not_found(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
    fake_card_progress_gateway: Mock,
    fake_access_service: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_card_progress_gateway.read_by_user_and_card.return_value = None
    handler = _handler(
        fake_current_user_service,
        fake_card_gateway,
        fake_deck_gateway,
        fake_user_gateway,
        fake_card_progress_gateway,
        fake_access_service,
    )

    # Act & Assert
    with pytest.raises(CardProgressNotFoundError):
        await handler(ReadCardProgressQuery(card_id=uuid4()))
