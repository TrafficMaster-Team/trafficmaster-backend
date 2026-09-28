import pytest

from trafficmaster.domain.card.errors.card import (
    EmptyAnswerOptionRationaleError,
    TooLongAnswerError,
    TooLongAnswerOptionRationaleError,
    TooShortAnswerError,
)
from trafficmaster.domain.card.values.answer_option import (
    MAX_ANSWER_OPTION_RATIONALE,
    MAX_ANSWER_OPTION_TEXT,
    AnswerOption,
)


def test_creates_answer_option() -> None:
    option = AnswerOption(text="Answer", is_correct=True, rationale="It matches the rule.")

    assert str(option) == "Answer"


@pytest.mark.parametrize("text", ["", "   "])
def test_rejects_empty_text(text: str) -> None:
    with pytest.raises(TooShortAnswerError):
        AnswerOption(text=text, is_correct=False, rationale="Explanation")


def test_rejects_too_long_text() -> None:
    with pytest.raises(TooLongAnswerError):
        AnswerOption(text="x" * (MAX_ANSWER_OPTION_TEXT + 1), is_correct=False, rationale="Explanation")


@pytest.mark.parametrize("rationale", ["", "   "])
def test_rejects_empty_rationale(rationale: str) -> None:
    with pytest.raises(EmptyAnswerOptionRationaleError):
        AnswerOption(text="Answer", is_correct=False, rationale=rationale)


def test_rejects_too_long_rationale() -> None:
    with pytest.raises(TooLongAnswerOptionRationaleError):
        AnswerOption(
            text="Answer",
            is_correct=False,
            rationale="x" * (MAX_ANSWER_OPTION_RATIONALE + 1),
        )
