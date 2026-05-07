from dataclasses import dataclass
from typing import TYPE_CHECKING

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import (
    NoPermissionToManageUserError,
    UserNotFoundByIdError,
)
from trafficmaster.domain.card.services.card_service import CardService
from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCardCommand:
    deck_id: DeckID
    question: str
    answer: str
    tags: list[str] | None = None


class CreateCardCommandHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        card_service: CardService,
        user_gateway: UserGateway,
        access_service: AccessService,
        transaction_manager: TransactionManager,
        deck_gateway: DeckGateway,
        card_gateway: CardGateway,
    ) -> None:
        self._card_service = card_service
        self._current_user_service = current_user_service
        self._user_gateway = user_gateway
        self._access_service = access_service
        self._transaction_manager = transaction_manager
        self._deck_gateway = deck_gateway
        self._card_gateway = card_gateway

    async def __call__(self, data: CreateCardCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()

        created_card: Card = self._card_service.create_card(
            deck_id=DeckID(data.deck_id),
            question=CardQuestion(data.question),
            answer=CardAnswer(data.answer),
            tags=[CardTag(tag) for tag in data.tags] if data.tags is not None else [],
        )
        deck: Deck | None = await self._deck_gateway.read_deck_by_id(DeckID(created_card.deck_id))

        if deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        user_card_handler: User | None = await self._user_gateway.read_by_id(user=UserID(deck.owner_id))

        if user_card_handler is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user_card_handler):
            msg = "You are not allowed to manage this card"
            raise NoPermissionToManageUserError(msg)

        await self._card_gateway.add(created_card)
        await self._transaction_manager.commit()
