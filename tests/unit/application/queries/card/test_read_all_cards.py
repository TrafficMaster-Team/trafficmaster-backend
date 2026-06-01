from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.views.card.read_by_id import ReadCardByIDView
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.queries.card.read_all_cards import (
    ReadAllCardsQuery,
    ReadAllCardsQueryHandler,
)


def _handler(
    cus: Mock, card_gateway: Mock, acl: Mock, deck_gateway: Mock, user_gateway: Mock
) -> ReadAllCardsQueryHandler:
    return ReadAllCardsQueryHandler(
        current_user_service=cus,
        card_gateway=card_gateway,
        access_service=acl,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
    )


def _query() -> ReadAllCardsQuery:
    return ReadAllCardsQuery(
        limit=10,
        offset=0,
        sorting_field="question",
        sorting_order=SortingOrder.ASC,
        deck_id=uuid4(),
    )


async def test_reads_all_cards_successfully(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck()
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_card_gateway.read_all_deck_cards.return_value = [create_card(), create_card()]
    handler = _handler(
        fake_current_user_service, fake_card_gateway, fake_access_service, fake_deck_gateway, fake_user_gateway
    )

    # Act
    result = await handler(_query())

    # Assert
    assert len(result) == 2
    assert all(isinstance(view, ReadCardByIDView) for view in result)


async def test_fails_when_deck_not_found(
    fake_current_user_service: Mock,
    fake_card_gateway: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service, fake_card_gateway, fake_access_service, fake_deck_gateway, fake_user_gateway
    )

    # Act & Assert
    with pytest.raises(DeckNotFoundError):
        await handler(_query())
    fake_card_gateway.read_all_deck_cards.assert_not_called()
