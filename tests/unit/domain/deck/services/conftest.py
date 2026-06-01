from typing import cast
from unittest.mock import create_autospec

import pytest

from trafficmaster.domain.deck.ports.deck_config_id_generator import DeckConfigIDGenerator
from trafficmaster.domain.deck.ports.deck_id_generator import DeckIDGenerator


@pytest.fixture
def deck_id_generator() -> DeckIDGenerator:
    return cast("DeckIDGenerator", create_autospec(DeckIDGenerator))


@pytest.fixture
def deck_config_id_generator() -> DeckConfigIDGenerator:
    return cast("DeckConfigIDGenerator", create_autospec(DeckConfigIDGenerator))
