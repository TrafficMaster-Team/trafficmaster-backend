from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.deck.create_deck import CreateDeckView
from trafficmaster.application.errors.deck import DeckConfigNotFoundError
from trafficmaster.application.errors.user import (
    NoPermissionToManageUserError,
    UserNotFoundByIdError,
)
from trafficmaster.domain.deck.services.deck_service import DeckService
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDeckCommand:
    owner_id: UUID
    deck_config_id: UUID
    title: str
    description: str | None = None
    is_public: bool = False


class CreateDeckCommandHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_gateway: UserGateway,
        access_service: AccessService,
        transaction_manager: TransactionManager,
        deck_gateway: DeckGateway,
        deck_config_gateway: DeckConfigGateway,
        deck_service: DeckService,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_service: Final[AccessService] = access_service
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._deck_service: Final[DeckService] = deck_service

    async def __call__(self, data: CreateDeckCommand) -> CreateDeckView:

        current_user: User = await self._current_user_service.get_current_user()

        user: User | None = await self._user_gateway.read_by_id(UserID(data.owner_id))

        if user is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You are not allowed to create a deck for this user"
            raise NoPermissionToManageUserError(msg)

        deck_config: DeckConfig | None = await self._deck_config_gateway.read_by_id(
            DeckConfigID(data.deck_config_id),
        )

        if deck_config is None:
            msg = "Deck config not found"
            raise DeckConfigNotFoundError(msg)

        if deck_config.owner_id != user.id:
            msg = "This deck config does not belong to the deck owner"
            raise NoPermissionToManageUserError(msg)

        created_deck: Deck = self._deck_service.create_deck(
            user_id=UserID(data.owner_id),
            title=DeckTitle(data.title),
            description=data.description,
            deck_config_id=deck_config.id,
            is_public=data.is_public,
        )

        await self._deck_gateway.add(created_deck)
        await self._transaction_manager.commit()

        return CreateDeckView(id=created_deck.id)
