import pytest

from trafficmaster.domain.deck.errors.deck import DeckTitleEmptyError
from trafficmaster.domain.deck.values.deck_title import DeckTitle


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("My Deck", id="typical"),
        pytest.param("a", id="single_char"),
    ],
)
def test_accepts_valid_title(value: str) -> None:
    sut = DeckTitle(value)

    assert sut.value == value
    assert str(sut) == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
    ],
)
def test_rejects_empty_title(value: str) -> None:
    with pytest.raises(DeckTitleEmptyError):
        DeckTitle(value)


def test_title_equality() -> None:
    assert DeckTitle("Deck") == DeckTitle("Deck")
    assert DeckTitle("Deck") != DeckTitle("Other")
