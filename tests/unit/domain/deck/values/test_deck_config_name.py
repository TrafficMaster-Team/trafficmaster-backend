import pytest

from trafficmaster.domain.deck.errors.deck_config import DeckConfigNameEmptyError
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("Default", id="typical"),
        pytest.param("a", id="single_char"),
    ],
)
def test_accepts_valid_name(value: str) -> None:
    sut = DeckConfigName(value)

    assert sut.value == value
    assert str(sut) == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
    ],
)
def test_rejects_empty_name(value: str) -> None:
    with pytest.raises(DeckConfigNameEmptyError):
        DeckConfigName(value)


def test_name_equality() -> None:
    assert DeckConfigName("Default") == DeckConfigName("Default")
    assert DeckConfigName("Default") != DeckConfigName("Custom")
