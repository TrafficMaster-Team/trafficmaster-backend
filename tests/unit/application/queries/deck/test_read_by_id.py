from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_deck_title
from trafficmaster.application.common.views.deck.read_by_id import ReadDeckByIDView
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError
from trafficmaster.application.queries.deck.read_by_id import ReadDeckByIdQuery, ReadDeckByIdQueryHandler


def _handler(cus: Mock, acl: Mock, deck_gateway: Mock, user_gateway: Mock) -> ReadDeckByIdQueryHandler:
    return ReadDeckByIdQueryHandler(
        current_user_service=cus,
        access_service=acl,
        deck_gateway=deck_gateway,
        user_gateway=user_gateway,
    )


async def test_reads_deck_successfully(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    deck = create_deck(title=create_deck_title("Geo"), is_public=False)
    fake_deck_gateway.read_by_id.return_value = deck
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_gateway, fake_user_gateway)

    # Act
    result = await handler(ReadDeckByIdQuery(deck_id=deck.id))

    # Assert
    assert isinstance(result, ReadDeckByIDView)
    assert result.id == deck.id
    assert result.title == "Geo"


async def test_fails_when_deck_not_found(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = None
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_gateway, fake_user_gateway)

    # Act & Assert
    with pytest.raises(DeckNotFoundError):
        await handler(ReadDeckByIdQuery(deck_id=uuid4()))


async def test_fails_for_private_deck_without_permission(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_deck_gateway: Mock,
    fake_user_gateway: Mock,
) -> None:
    # Arrange
    fake_deck_gateway.read_by_id.return_value = create_deck(is_public=False)
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(fake_current_user_service, fake_access_service, fake_deck_gateway, fake_user_gateway)

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(ReadDeckByIdQuery(deck_id=uuid4()))
