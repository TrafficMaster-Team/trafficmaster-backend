from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, Mock, create_autospec

import pytest

from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.services.auth_session import AuthSessionService
from trafficmaster.domain.card.services.card_service import CardService
from trafficmaster.domain.card_progress.services.card_progress_service import CardProgressService
from trafficmaster.domain.deck.services.deck_config_service import DeckConfigService
from trafficmaster.domain.deck.services.deck_service import DeckService
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.services.user_service import UserService


@pytest.fixture
def fake_transaction_manager() -> Mock:
    fake = Mock()
    fake.commit = AsyncMock()
    fake.flush = AsyncMock()
    fake.rollback = AsyncMock()
    return fake


@pytest.fixture
def fake_user_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    fake.read_by_email = AsyncMock(return_value=None)
    fake.read_all_users = AsyncMock(return_value=[])
    return fake


@pytest.fixture
def fake_current_user_service() -> Mock:
    fake = Mock()
    fake.get_current_user = AsyncMock(return_value=create_user())
    return fake


@pytest.fixture
def fake_user_service() -> Mock:
    return cast("Mock", create_autospec(UserService))


@pytest.fixture
def fake_access_service() -> Mock:
    fake = cast("Mock", create_autospec(AccessService))
    fake.can_manage_user.return_value = True
    return fake


@pytest.fixture
def fake_card_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.delete_by_deck_id = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    fake.read_all_deck_cards = AsyncMock(return_value=[])
    fake.read_all_by_deck = AsyncMock(return_value=[])
    fake.count_by_deck = AsyncMock(return_value=0)
    fake.count_by_user = AsyncMock(return_value=0)
    return fake


@pytest.fixture
def fake_deck_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    fake.read_by_user_id = AsyncMock(return_value=[])
    fake.read_public_decks = AsyncMock(return_value=[])
    fake.count_by_user = AsyncMock(return_value=0)
    fake.exists_with_deck_config_id = AsyncMock(return_value=False)
    return fake


@pytest.fixture
def fake_card_service() -> Mock:
    return cast("Mock", create_autospec(CardService))


@pytest.fixture
def fake_deck_config_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    fake.read_by_user_id = AsyncMock(return_value=[])
    return fake


@pytest.fixture
def fake_card_progress_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    fake.read_by_user_and_card = AsyncMock(return_value=None)
    fake.read_due_learning = AsyncMock(return_value=[])
    fake.read_due_review = AsyncMock(return_value=[])
    fake.read_new_cards = AsyncMock(return_value=[])
    fake.count_by_state = AsyncMock(return_value={})
    fake.count_due_learning = AsyncMock(return_value=0)
    fake.count_due_review = AsyncMock(return_value=0)
    return fake


@pytest.fixture
def fake_review_log_gateway() -> Mock:
    fake = Mock()
    fake.add = AsyncMock()
    fake.delete_by_id = AsyncMock()
    fake.count_new_done = AsyncMock(return_value=0)
    fake.count_reviews_done = AsyncMock(return_value=0)
    fake.read_by_card = AsyncMock(return_value=[])
    fake.read_by_user = AsyncMock(return_value=[])
    return fake


@pytest.fixture
def fake_card_progress_service() -> Mock:
    return cast("Mock", create_autospec(CardProgressService))


@pytest.fixture
def fake_clock() -> Mock:
    clock = Mock()
    clock.current_time = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
    clock.today_start = datetime(2026, 6, 1, 0, 0, tzinfo=UTC)
    return clock


@pytest.fixture
def fake_deck_service() -> Mock:
    return cast("Mock", create_autospec(DeckService))


@pytest.fixture
def fake_deck_config_service() -> Mock:
    return cast("Mock", create_autospec(DeckConfigService))


@pytest.fixture
def fake_auth_session_service() -> Mock:
    return cast("Mock", create_autospec(AuthSessionService))
