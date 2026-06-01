from typing import cast
from unittest.mock import create_autospec

import pytest

from trafficmaster.domain.user.ports.id_generator import UserIDGenerator
from trafficmaster.domain.user.ports.password_hasher import PasswordHasher


@pytest.fixture
def id_generator() -> UserIDGenerator:
    return cast("UserIDGenerator", create_autospec(UserIDGenerator))


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return cast("PasswordHasher", create_autospec(PasswordHasher))
