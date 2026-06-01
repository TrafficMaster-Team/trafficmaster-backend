import pytest

from trafficmaster.domain.card.errors.card import (
    CardQuestionEmptyError,
    TooLongQuestionError,
)
from trafficmaster.domain.card.values.card_question import MAXIMUM_CARD_QUESTION, CardQuestion


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("What is the capital of France?", id="typical"),
        pytest.param("a", id="min_len"),
        pytest.param("a" * MAXIMUM_CARD_QUESTION, id="max_len"),
    ],
)
def test_accepts_valid_question(value: str) -> None:
    sut = CardQuestion(value)

    assert sut.value == value
    assert str(sut) == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
    ],
)
def test_rejects_empty_question(value: str) -> None:
    with pytest.raises(CardQuestionEmptyError):
        CardQuestion(value)


def test_rejects_too_long_question() -> None:
    with pytest.raises(TooLongQuestionError):
        CardQuestion("a" * (MAXIMUM_CARD_QUESTION + 1))


def test_question_equality() -> None:
    assert CardQuestion("Q?") == CardQuestion("Q?")
    assert CardQuestion("Q?") != CardQuestion("A?")
