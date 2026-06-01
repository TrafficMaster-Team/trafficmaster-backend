import pytest

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.values import (
    create_deck_config_id,
    create_deck_id,
    create_deck_title,
    create_user_id,
)
from trafficmaster.domain.common.errors import DomainError
from trafficmaster.domain.deck.entities.deck import Deck


def test_creates_deck_with_given_values() -> None:
    # Arrange
    deck_id = create_deck_id()
    owner_id = create_user_id()
    config_id = create_deck_config_id()
    title = create_deck_title("History")

    # Act
    sut = create_deck(
        deck_id=deck_id,
        owner_id=owner_id,
        deck_config_id=config_id,
        title=title,
        description="desc",
        is_public=True,
    )

    # Assert
    assert sut.id == deck_id
    assert sut.owner_id == owner_id
    assert sut.deck_config_id == config_id
    assert sut.title == title
    assert sut.description == "desc"
    assert sut.is_public is True


def test_deck_is_private_by_default() -> None:
    sut = create_deck()

    assert sut.is_public is False


def test_deck_id_cannot_be_changed() -> None:
    sut = create_deck()

    with pytest.raises(DomainError):
        sut.id = create_deck_id()


def test_change_title() -> None:
    sut = create_deck()
    new_title = create_deck_title("New Title")

    sut.change_title(new_title)

    assert sut.title == new_title


@pytest.mark.parametrize("description", [pytest.param("new desc", id="set"), pytest.param(None, id="cleared")])
def test_change_description(description: str | None) -> None:
    sut = create_deck(description="old")

    sut.change_description(description)

    assert sut.description == description


@pytest.mark.parametrize("is_public", [True, False])
def test_change_privacy(is_public: bool) -> None:
    sut = create_deck(is_public=not is_public)

    sut.change_privacy(is_public)

    assert sut.is_public is is_public


def test_assign_deck_config() -> None:
    sut = create_deck()
    new_config_id = create_deck_config_id()

    sut.assign_deck_config(new_config_id)

    assert sut.deck_config_id == new_config_id


def test_serialize_deserialize_roundtrip() -> None:
    # Arrange
    original = create_deck(title=create_deck_title("Roundtrip"), description="d", is_public=True)

    # Act
    restored = Deck.deserialize(original.serialize())

    # Assert
    assert restored.id == original.id
    assert restored.owner_id == original.owner_id
    assert restored.deck_config_id == original.deck_config_id
    assert restored.title == original.title
    assert restored.description == original.description
    assert restored.is_public == original.is_public
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at


def test_serialize_handles_none_description() -> None:
    sut = create_deck(description=None)

    assert sut.serialize()["description"] is None


def test_decks_with_same_id_are_equal() -> None:
    same_id = create_deck_id()
    deck1 = create_deck(deck_id=same_id, title=create_deck_title("A"))
    deck2 = create_deck(deck_id=same_id, title=create_deck_title("B"))

    assert deck1 == deck2
    assert hash(deck1) == hash(deck2)
