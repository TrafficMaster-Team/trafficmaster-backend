from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.unit.factories.card_entity import create_card
from tests.unit.factories.deck_entity import create_deck
from tests.unit.factories.user_entity import create_user
from tests.unit.factories.values import create_card_answer, create_card_question, create_card_tag
from trafficmaster.application.common.views.card.read_by_id import ReadCardByIDView
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError
from trafficmaster.application.queries.card.read_by_id import (
    ReadCardByIdQuery,
    ReadCardByIdQueryHandler,
)


def _handler(
    cus: Mock, acl: Mock, card_gateway: Mock, user_gateway: Mock, deck_gateway: Mock
) -> ReadCardByIdQueryHandler:
    return ReadCardByIdQueryHandler(
        current_user_service=cus,
        access_service=acl,
        card_gateway=card_gateway,
        user_gateway=user_gateway,
        deck_gateway=deck_gateway,
    )


async def test_reads_card_successfully(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_card_gateway: Mock,
    fake_user_gateway: Mock,
    fake_deck_gateway: Mock,
) -> None:
    # Arrange
    card = create_card(
        question=create_card_question("What?"),
        answer=create_card_answer("That"),
        tags=[create_card_tag("tag")],
    )
    fake_card_gateway.read_by_id.return_value = card
    fake_deck_gateway.read_by_id.return_value = create_deck(is_public=False)
    fake_user_gateway.read_by_id.return_value = create_user()
    handler = _handler(
        fake_current_user_service, fake_access_service, fake_card_gateway, fake_user_gateway, fake_deck_gateway
    )

    # Act
    result = await handler(ReadCardByIdQuery(card_id=card.id))

    # Assert
    assert isinstance(result, ReadCardByIDView)
    assert result.id == card.id
    assert result.question == "What?"
    assert result.answer == "That"
    assert result.tags == ["tag"]


async def test_fails_when_card_not_found(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_card_gateway: Mock,
    fake_user_gateway: Mock,
    fake_deck_gateway: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = None
    handler = _handler(
        fake_current_user_service, fake_access_service, fake_card_gateway, fake_user_gateway, fake_deck_gateway
    )

    # Act & Assert
    with pytest.raises(CardNotFoundError):
        await handler(ReadCardByIdQuery(card_id=uuid4()))


async def test_fails_for_private_deck_without_permission(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_card_gateway: Mock,
    fake_user_gateway: Mock,
    fake_deck_gateway: Mock,
) -> None:
    # Arrange
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck(is_public=False)
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service, fake_access_service, fake_card_gateway, fake_user_gateway, fake_deck_gateway
    )

    # Act & Assert
    with pytest.raises(NoPermissionToManageUserError):
        await handler(ReadCardByIdQuery(card_id=uuid4()))


async def test_reads_public_deck_card_without_permission(
    fake_current_user_service: Mock,
    fake_access_service: Mock,
    fake_card_gateway: Mock,
    fake_user_gateway: Mock,
    fake_deck_gateway: Mock,
) -> None:
    # Arrange: public deck bypasses the permission check
    fake_card_gateway.read_by_id.return_value = create_card()
    fake_deck_gateway.read_by_id.return_value = create_deck(is_public=True)
    fake_user_gateway.read_by_id.return_value = create_user()
    fake_access_service.can_manage_user.return_value = False
    handler = _handler(
        fake_current_user_service, fake_access_service, fake_card_gateway, fake_user_gateway, fake_deck_gateway
    )

    # Act
    result = await handler(ReadCardByIdQuery(card_id=uuid4()))

    # Assert
    assert isinstance(result, ReadCardByIDView)
