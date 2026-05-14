from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.card_progress import CardProgressNotFoundError
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ResetCardProgressCommand:
    card_id: UUID


class ResetCardProgressCommandHandler:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        card_gateway: CardGateway,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
        card_progress_gateway: CardProgressGateway,
        current_user_service: CurrentUserService,
        access_service: AccessService,
    ) -> None:
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._card_gateway: Final[CardGateway] = card_gateway
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._card_progress_gateway: Final[CardProgressGateway] = card_progress_gateway
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service

    async def __call__(self, data: ResetCardProgressCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()

        card: Card | None = await self._card_gateway.read_by_id(CardID(data.card_id))

        if card is None:
            msg = "Card not found"
            raise CardNotFoundError(msg)

        deck: Deck | None = await self._deck_gateway.read_by_id(DeckID(card.deck_id))

        if deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        deck_owner: User | None = await self._user_gateway.read_by_id(UserID(deck.owner_id))

        if deck_owner is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not deck.is_public and not self._access_service.can_manage_user(
            subject=current_user,
            target=deck_owner,
        ):
            msg = "You don't have access to this card"
            raise NoPermissionToManageUserError(msg)

        progress: CardProgress | None = await self._card_progress_gateway.read_by_user_and_card(
            user_id=current_user.id,
            card_id=card.id,
        )

        if progress is None:
            msg = "Card progress not found"
            raise CardProgressNotFoundError(msg)

        await self._card_progress_gateway.delete_by_id(progress.id)
        await self._transaction_manager.commit()
