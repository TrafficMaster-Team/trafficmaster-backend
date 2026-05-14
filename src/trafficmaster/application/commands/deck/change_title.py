from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeTitleCommand:
    deck_id: UUID
    title: str


class ChangeTitleCommandHandler:
    def __init__(
        self,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
        transaction_manager: TransactionManager,
        current_user_service: CurrentUserService,
        access_service: AccessService,
    ) -> None:
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service

    async def __call__(self, data: ChangeTitleCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()

        deck: Deck | None = await self._deck_gateway.read_by_id(DeckID(data.deck_id))

        if deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        user: User | None = await self._user_gateway.read_by_id(UserID(deck.owner_id))

        if user is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You are not allowed to manage this deck"
            raise NoPermissionToManageUserError(msg)

        deck.change_title(DeckTitle(data.title))

        await self._transaction_manager.commit()
