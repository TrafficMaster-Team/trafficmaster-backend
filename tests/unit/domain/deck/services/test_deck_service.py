from unittest.mock import Mock

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.values import (
    create_deck_config_id,
    create_deck_id,
    create_deck_title,
    create_user_id,
)
from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.services.deck_service import DeckService


def test_creates_deck_with_generated_id(deck_id_generator: Mock) -> None:
    # Arrange
    expected_id = create_deck_id()
    deck_id_generator.return_value = expected_id

    user_id = create_user_id()
    title = create_deck_title("New Deck")
    config_id = create_deck_config_id()
    sut = DeckService(deck_id_generator=deck_id_generator)

    # Act
    result = sut.create_deck(
        user_id=user_id,
        title=title,
        description="desc",
        deck_config_id=config_id,
        is_public=True,
    )

    # Assert
    assert isinstance(result, Deck)
    assert result.id == expected_id
    assert result.owner_id == user_id
    assert result.title == title
    assert result.description == "desc"
    assert result.deck_config_id == config_id
    assert result.is_public is True


def test_copies_deck_for_new_owner(deck_id_generator: Mock) -> None:
    # Arrange
    new_id = create_deck_id()
    deck_id_generator.return_value = new_id
    original = create_deck(description="original", is_public=False)
    new_user_id = create_user_id()
    new_config_id = create_deck_config_id()
    sut = DeckService(deck_id_generator=deck_id_generator)

    # Act
    result = sut.copy_deck(
        original,
        new_user_id=new_user_id,
        new_deck_config_id=new_config_id,
        is_public=True,
    )

    # Assert
    assert result.id == new_id
    assert result.owner_id == new_user_id
    assert result.deck_config_id == new_config_id
    assert result.title == original.title
    assert result.description == original.description
    assert result.is_public is True
