from unittest.mock import Mock

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.values import (
    create_answer_option,
    create_card_hint,
    create_card_id,
    create_card_question,
    create_card_tag,
    create_deck_id,
)
from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.services.card_service import CardService


def test_creates_card_with_generated_id(card_id_generator: Mock) -> None:
    # Arrange
    expected_id = create_card_id()
    card_id_generator.return_value = expected_id

    deck_id = create_deck_id()
    question = create_card_question("Q?")
    answer_options = [create_answer_option(text="A", rationale="A is correct")]
    hint = create_card_hint("A useful hint")
    tag = create_card_tag("tag")
    sut = CardService(id_generator=card_id_generator)

    # Act
    result = sut.create_card(
        deck_id=deck_id,
        question=question,
        answer_options=answer_options,
        hint=hint,
        tags=[tag],
        image_path="/img.png",
    )

    # Assert
    assert isinstance(result, Card)
    assert result.id == expected_id
    assert result.deck_id == deck_id
    assert result.question == question
    assert result.answer_options == answer_options
    assert result.hint == hint
    assert result.tags == [tag]
    assert result.image_path == "/img.png"


def test_creates_card_with_empty_tags_by_default(card_id_generator: Mock) -> None:
    # Arrange
    card_id_generator.return_value = create_card_id()
    sut = CardService(id_generator=card_id_generator)

    # Act
    result = sut.create_card(
        deck_id=create_deck_id(),
        question=create_card_question(),
        answer_options=[create_answer_option()],
        hint=create_card_hint(),
    )

    # Assert
    assert result.tags == []
    assert result.image_path is None


def test_copies_card_into_another_deck(card_id_generator: Mock) -> None:
    # Arrange
    new_id = create_card_id()
    card_id_generator.return_value = new_id
    original = create_card(tags=[create_card_tag("a"), create_card_tag("b")], image_path="/p.png")
    new_deck_id = create_deck_id()
    sut = CardService(id_generator=card_id_generator)

    # Act
    result = sut.copy_card(original, new_deck_id)

    # Assert
    assert result.id == new_id
    assert result.deck_id == new_deck_id
    assert result.question == original.question
    assert result.answer_options == original.answer_options
    assert result.answer_options is not original.answer_options
    assert result.hint == original.hint
    assert result.image_path == original.image_path
    assert result.tags == original.tags
    assert result.tags is not original.tags
