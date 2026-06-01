from unittest.mock import Mock

from tests.unit.factories.deck_config_entity import create_deck_config
from tests.unit.factories.values import (
    create_advanced_config,
    create_daily_limits,
    create_deck_config_id,
    create_deck_config_name,
    create_lapses_config,
    create_new_cards_config,
    create_user_id,
)
from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.services.deck_config_service import DeckConfigService


def test_creates_config_with_generated_id(deck_config_id_generator: Mock) -> None:
    # Arrange
    expected_id = create_deck_config_id()
    deck_config_id_generator.return_value = expected_id

    owner_id = create_user_id()
    name = create_deck_config_name("Custom")
    daily_limits = create_daily_limits()
    new_cards = create_new_cards_config()
    lapses = create_lapses_config()
    advanced = create_advanced_config()
    sut = DeckConfigService(id_generator=deck_config_id_generator)

    # Act
    result = sut.create_config(
        owner_id=owner_id,
        name=name,
        daily_limits=daily_limits,
        new_cards=new_cards,
        lapses=lapses,
        advanced=advanced,
    )

    # Assert
    assert isinstance(result, DeckConfig)
    assert result.id == expected_id
    assert result.owner_id == owner_id
    assert result.name == name
    assert result.daily_limits == daily_limits
    assert result.new_cards == new_cards
    assert result.lapses == lapses
    assert result.advanced == advanced


def test_copies_config_for_new_owner(deck_config_id_generator: Mock) -> None:
    # Arrange
    new_id = create_deck_config_id()
    deck_config_id_generator.return_value = new_id
    original = create_deck_config()
    new_owner_id = create_user_id()
    sut = DeckConfigService(id_generator=deck_config_id_generator)

    # Act
    result = sut.copy_config(original, new_owner_id)

    # Assert
    assert result.id == new_id
    assert result.owner_id == new_owner_id
    assert result.name == original.name
    assert result.daily_limits == original.daily_limits
    assert result.new_cards == original.new_cards
    assert result.lapses == original.lapses
    assert result.advanced == original.advanced
