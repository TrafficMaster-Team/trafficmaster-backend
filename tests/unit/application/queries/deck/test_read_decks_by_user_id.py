from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from trafficmaster.application.common.views.deck.read_by_id import ReadDeckByIDView
from trafficmaster.application.errors.user import UserNotFoundByIdError
from trafficmaster.application.queries.deck.read_decks_by_user_id import (
    ReadDecksByUserIdQuery,
    ReadDecksByUserIdQueryHandler,
)


def _handler(cus: Mock, acl: Mock, deck_gateway: Mock, user_gateway: Mock) -> ReadDecksByUserIdQueryHandler:
    return ReadDecksByUserIdQueryHandler(
        current_user_service=cus,
        access_service=acl,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
    )


async def test_reads_decks_by_user(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_deck_gateway.read_by_user_id.return_value = [create_deck(), create_deck()]
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_gateway, fake_user_gateway)

    # Act
    result = await handler(ReadDecksByUserIdQuery(user_id=uuid4()))

    # Assert
    assert len(result) == 2
    assert all(isinstance(view, ReadDeckByIDView) for view in result)


async def test_fails_when_user_not_found(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_user_gateway.read_by_id.return_value = None
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_gateway, fake_user_gateway)

    # Act & Assert
    with pytest.raises(UserNotFoundByIdError):
        await handler(ReadDecksByUserIdQuery(user_id=uuid4()))
