import pytest

from trafficmaster.domain.card.errors.card import EmptyCardTagError, TooLongCardTagError
from trafficmaster.domain.card.values.card_tag import MAXIMUM_CARD_TAG, CardTag


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("geography", id="typical"),
        pytest.param("a", id="min_len"),
        pytest.param("a" * MAXIMUM_CARD_TAG, id="max_len"),
    ],
)
def test_accepts_valid_tag(value: str) -> None:
    sut = CardTag(value)

    assert sut.value == value
    assert str(sut) == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
    ],
)
def test_rejects_empty_tag(value: str) -> None:
    with pytest.raises(EmptyCardTagError):
        CardTag(value)


def test_rejects_too_long_tag() -> None:
    with pytest.raises(TooLongCardTagError):
        CardTag("a" * (MAXIMUM_CARD_TAG + 1))


def test_tag_equality_and_hash() -> None:
    assert CardTag("math") == CardTag("math")
    assert hash(CardTag("math")) == hash(CardTag("math"))
    assert CardTag("math") != CardTag("history")
