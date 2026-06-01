import pytest

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.values import (
    create_advanced_config,
    create_daily_limits,
    create_deck_config_id,
    create_deck_config_name,
    create_lapses_config,
    create_new_cards_config,
)
from trafficmaster.domain.common.errors import DomainError
from trafficmaster.domain.deck.entities.deck_config import DeckConfig


def test_creates_deck_config_with_given_values() -> None:
    # Arrange
    config_id = create_deck_config_id()
    name = create_deck_config_name("Custom")
    daily = create_daily_limits(new_cards_per_day=10, max_reviews_per_day=100)

    # Act
    sut = create_deck_config(config_id=config_id, name=name, daily_limits=daily)

    # Assert
    assert sut.id == config_id
    assert sut.name == name
    assert sut.daily_limits == daily


def test_deck_config_id_cannot_be_changed() -> None:
    sut = create_deck_config()

    with pytest.raises(DomainError):
        sut.id = create_deck_config_id()


def test_change_config_name() -> None:
    sut = create_deck_config()
    new_name = create_deck_config_name("Renamed")

    sut.change_config_name(new_name)

    assert sut.name == new_name


def test_change_daily_limits() -> None:
    sut = create_deck_config()
    new_limits = create_daily_limits(new_cards_per_day=5, max_reviews_per_day=50)

    sut.change_daily_limits(new_limits)

    assert sut.daily_limits == new_limits


def test_change_new_cards() -> None:
    sut = create_deck_config()
    new_cards = create_new_cards_config(learning_steps=[5, 15])

    sut.change_new_cards(new_cards)

    assert sut.new_cards == new_cards


def test_change_lapses() -> None:
    sut = create_deck_config()
    new_lapses = create_lapses_config(relearning_steps=[20])

    sut.change_lapses(new_lapses)

    assert sut.lapses == new_lapses


def test_change_advanced() -> None:
    sut = create_deck_config()
    new_advanced = create_advanced_config(max_interval=1000)

    sut.change_advanced(new_advanced)

    assert sut.advanced == new_advanced


def test_serialize_deserialize_roundtrip() -> None:
    # Arrange
    original = create_deck_config()

    # Act
    restored = DeckConfig.deserialize(original.serialize())

    # Assert
    assert restored.id == original.id
    assert restored.owner_id == original.owner_id
    assert restored.name == original.name
    assert restored.daily_limits == original.daily_limits
    assert restored.new_cards == original.new_cards
    assert restored.lapses == original.lapses
    assert restored.advanced == original.advanced
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at
