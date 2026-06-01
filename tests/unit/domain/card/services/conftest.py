from typing import cast
from unittest.mock import create_autospec

import pytest

from trafficmaster.domain.card.ports.card_id_generator import CardIDGenerator


@pytest.fixture
def card_id_generator() -> CardIDGenerator:
    return cast("CardIDGenerator", create_autospec(CardIDGenerator))
