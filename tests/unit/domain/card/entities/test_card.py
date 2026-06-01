import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.values import (
    create_card_answer,
    create_card_id,
    create_card_question,
    create_card_tag,
    create_deck_id,
)
from trafficmaster.domain.card.errors.card import CardTagNotFoundError, DuplicateCardTagError
from trafficmaster.domain.common.errors import DomainError


def test_creates_card_with_given_values() -> None:
    # Arrange
    deck_id = create_deck_id()
    question = create_card_question("Q?")
    answer = create_card_answer("A")
    tag = create_card_tag("tag")

    # Act
    sut = create_card(deck_id=deck_id, question=question, answer=answer, tags=[tag], image_path="/img.png")

    # Assert
    assert sut.deck_id == deck_id
    assert sut.question == question
    assert sut.answer == answer
    assert sut.tags == [tag]
    assert sut.image_path == "/img.png"


def test_card_tags_default_to_empty_list() -> None:
    sut = create_card()

    assert sut.tags == []


def test_card_id_cannot_be_changed() -> None:
    sut = create_card()

    with pytest.raises(DomainError):
        sut.id = create_card_id()


def test_change_deck_updates_timestamp() -> None:
    # Arrange
    sut = create_card()
    new_deck_id = create_deck_id()
    before = sut.updated_at

    # Act
    sut.change_deck(new_deck_id)

    # Assert
    assert sut.deck_id == new_deck_id
    assert sut.updated_at >= before


def test_change_question() -> None:
    sut = create_card()
    new_question = create_card_question("New question?")

    sut.change_question(new_question)

    assert sut.question == new_question


def test_change_answer() -> None:
    sut = create_card()
    new_answer = create_card_answer("New answer")

    sut.change_answer(new_answer)

    assert sut.answer == new_answer


@pytest.mark.parametrize("image_path", [pytest.param("/path.png", id="set"), pytest.param(None, id="cleared")])
def test_change_image_path(image_path: str | None) -> None:
    sut = create_card(image_path="/old.png")

    sut.change_image_path(image_path)

    assert sut.image_path == image_path


def test_add_tag() -> None:
    sut = create_card()
    tag = create_card_tag("new-tag")

    sut.add_tag(tag)

    assert tag in sut.tags


def test_add_duplicate_tag_raises() -> None:
    tag = create_card_tag("dup")
    sut = create_card(tags=[tag])

    with pytest.raises(DuplicateCardTagError):
        sut.add_tag(tag)


def test_remove_tag() -> None:
    tag = create_card_tag("removable")
    sut = create_card(tags=[tag])

    sut.remove_tag(tag)

    assert tag not in sut.tags


def test_remove_missing_tag_raises() -> None:
    sut = create_card()

    with pytest.raises(CardTagNotFoundError):
        sut.remove_tag(create_card_tag("missing"))


def test_cards_with_same_id_are_equal() -> None:
    same_id = create_card_id()
    card1 = create_card(card_id=same_id, question=create_card_question("Q1?"))
    card2 = create_card(card_id=same_id, question=create_card_question("Q2?"))

    assert card1 == card2
    assert hash(card1) == hash(card2)


def test_cards_with_different_id_are_not_equal() -> None:
    assert create_card(card_id=create_card_id()) != create_card(card_id=create_card_id())


def test_card_can_be_used_in_set() -> None:
    same_id = create_card_id()
    card1 = create_card(card_id=same_id)
    card2 = create_card(card_id=same_id)
    card3 = create_card(card_id=create_card_id())

    assert len({card1, card2, card3}) == 2
