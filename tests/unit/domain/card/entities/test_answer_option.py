import pytest

from tests.unit.factories.values import create_answer_option, create_answer_option_id
from trafficmaster.domain.card.entities.answer_option import (
    MAX_ANSWER_OPTION_RATIONALE,
    MAX_ANSWER_OPTION_TEXT,
)
from trafficmaster.domain.card.errors.card import (
    TooLongAnswerError,
    TooLongAnswerOptionRationaleError,
    TooShortAnswerError,
)


def test_creates_answer_option() -> None:
    option = create_answer_option(text="Answer", rationale="It matches the rule.")

    assert str(option) == "Answer"


@pytest.mark.parametrize("text", ["", "   "])
def test_rejects_empty_text(text: str) -> None:
    with pytest.raises(TooShortAnswerError):
        create_answer_option(text=text, is_correct=False, rationale="Explanation")


def test_rejects_too_long_text() -> None:
    with pytest.raises(TooLongAnswerError):
        create_answer_option(
            text="x" * (MAX_ANSWER_OPTION_TEXT + 1),
            is_correct=False,
            rationale="Explanation",
        )


@pytest.mark.parametrize("rationale", ["", "   "])
def test_allows_empty_rationale(rationale: str) -> None:
    option = create_answer_option(text="Answer", is_correct=False, rationale=rationale)

    assert option.rationale == rationale


def test_rejects_too_long_rationale() -> None:
    with pytest.raises(TooLongAnswerOptionRationaleError):
        create_answer_option(
            text="Answer",
            is_correct=False,
            rationale="x" * (MAX_ANSWER_OPTION_RATIONALE + 1),
        )


def test_answer_options_with_same_id_are_equal() -> None:
    option_id = create_answer_option_id()

    first = create_answer_option(option_id=option_id, text="First")
    second = create_answer_option(option_id=option_id, text="Changed")

    assert first == second
    assert hash(first) == hash(second)


def test_answer_options_with_different_ids_are_not_equal() -> None:
    assert create_answer_option() != create_answer_option()
