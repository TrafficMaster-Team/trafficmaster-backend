from typing import cast
from unittest.mock import create_autospec

import pytest

from trafficmaster.domain.card_progress.ports.card_progress_id_generator import CardProgressIDGenerator
from trafficmaster.domain.card_progress.ports.review_id_generator import ReviewIDGenerator


@pytest.fixture
def card_progress_id_generator() -> CardProgressIDGenerator:
    return cast("CardProgressIDGenerator", create_autospec(CardProgressIDGenerator))


@pytest.fixture
def review_id_generator() -> ReviewIDGenerator:
    return cast("ReviewIDGenerator", create_autospec(ReviewIDGenerator))
