import pytest

from trafficmaster.domain.card.errors.card import EmptyCardHintError, TooLongCardHintError
from trafficmaster.domain.card.values.card_hint import MAX_CARD_HINT, CardHint


def test_creates_hint() -> None:
    assert str(CardHint("Remember the definition.")) == "Remember the definition."


@pytest.mark.parametrize("hint", ["", "   "])
def test_rejects_empty_hint(hint: str) -> None:
    with pytest.raises(EmptyCardHintError):
        CardHint(hint)


def test_rejects_too_long_hint() -> None:
    with pytest.raises(TooLongCardHintError):
        CardHint("x" * (MAX_CARD_HINT + 1))
