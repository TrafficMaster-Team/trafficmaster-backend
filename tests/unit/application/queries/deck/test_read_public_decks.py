from unittest.mock import Mock

from tests.unit.factories.deck_entity import create_deck
from trafficmaster.application.common.views.deck.public_deck import PublicDeckView
from trafficmaster.application.queries.deck.read_public_decks import (
    ReadPublicDecksQuery,
    ReadPublicDecksQueryHandler,
)


async def test_reads_public_decks(fake_deck_gateway: Mock) -> None:
    # Arrange
    fake_deck_gateway.read_public_decks.return_value = [create_deck(is_public=True), create_deck(is_public=True)]
    handler = ReadPublicDecksQueryHandler(deck_gateway=fake_deck_gateway)

    # Act
    result = await handler(ReadPublicDecksQuery(limit=10, offset=0))

    # Assert
    assert len(result) == 2
    assert all(isinstance(view, PublicDeckView) for view in result)


async def test_returns_empty_list_when_no_public_decks(fake_deck_gateway: Mock) -> None:
    # Arrange
    fake_deck_gateway.read_public_decks.return_value = []
    handler = ReadPublicDecksQueryHandler(deck_gateway=fake_deck_gateway)

    # Act
    result = await handler(ReadPublicDecksQuery())

    # Assert
    assert result == []
