from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class RemoveTagCommand:
    card_id: UUID

    tag: str


class RemoveTagCommandHandler:
    def __init__(
        self,
        card_gateway: CardGateway,
        transaction_manager: TransactionManager,
        current_user_service: CurrentUserService,
        access_service: AccessService,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
    ) -> None:
        self._card_gateway: Final[CardGateway] = card_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway

    async def __call__(self, data: RemoveTagCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()
        card: Card | None = await self._card_gateway.read_by_id(CardID(data.card_id))

        if card is None:
            msg = "Card not found"
            raise CardNotFoundError(msg)

        deck: Deck | None = await self._deck_gateway.read_by_id(DeckID(card.deck_id))

        if deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        user_card_handler: User | None = await self._user_gateway.read_by_id(user_id=UserID(deck.owner_id))

        if user_card_handler is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user_card_handler):
            msg = "You are not allowed to manage this card"
            raise NoPermissionToManageUserError(msg)

        card.remove_tag(tag=CardTag(data.tag))

        await self._transaction_manager.commit()
