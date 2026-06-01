import pytest

from trafficmaster.domain.card.errors.card import CardAnswerEmptyError, TooLongAnswerError
from trafficmaster.domain.card.values.card_answer import MAXIMUM_CARD_ANSWER, CardAnswer


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("Paris", id="typical"),
        pytest.param("a", id="min_len"),
        pytest.param("a" * MAXIMUM_CARD_ANSWER, id="max_len"),
    ],
)
def test_accepts_valid_answer(value: str) -> None:
    sut = CardAnswer(value)

    assert sut.value == value
    assert str(sut) == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
    ],
)
def test_rejects_empty_answer(value: str) -> None:
    with pytest.raises(CardAnswerEmptyError):
        CardAnswer(value)


def test_rejects_too_long_answer() -> None:
    with pytest.raises(TooLongAnswerError):
        CardAnswer("a" * (MAXIMUM_CARD_ANSWER + 1))


def test_answer_equality() -> None:
    assert CardAnswer("Paris") == CardAnswer("Paris")
    assert CardAnswer("Paris") != CardAnswer("London")
