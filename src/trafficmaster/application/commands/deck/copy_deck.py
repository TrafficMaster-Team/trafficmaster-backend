from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.deck.copy_deck import CopyDeckView
from trafficmaster.application.errors.deck import DeckConfigNotFoundError, DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.card.services.card_service import CardService
from trafficmaster.domain.deck.services.deck_config_service import DeckConfigService
from trafficmaster.domain.deck.services.deck_service import DeckService
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class CopyDeckCommand:
    source_deck_id: UUID


class CopyDeckCommandHandler:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        current_user_service: CurrentUserService,
        deck_gateway: DeckGateway,
        deck_config_gateway: DeckConfigGateway,
        card_gateway: CardGateway,
        user_gateway: UserGateway,
        access_service: AccessService,
        deck_service: DeckService,
        deck_config_service: DeckConfigService,
        card_service: CardService,
    ) -> None:
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._card_gateway: Final[CardGateway] = card_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_service: Final[AccessService] = access_service
        self._deck_service: Final[DeckService] = deck_service
        self._deck_config_service: Final[DeckConfigService] = deck_config_service
        self._card_service: Final[CardService] = card_service

    async def __call__(self, data: CopyDeckCommand) -> CopyDeckView:
        current_user: User = await self._current_user_service.get_current_user()

        source_deck: Deck | None = await self._deck_gateway.read_deck_by_id(DeckID(data.source_deck_id))

        if source_deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        source_owner: User | None = await self._user_gateway.read_by_id(UserID(source_deck.owner_id))

        if source_owner is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not source_deck.is_public and not self._access_service.can_manage_user(
            subject=current_user,
            target=source_owner,
        ):
            msg = "You don't have access to this deck"
            raise NoPermissionToManageUserError(msg)

        source_config: DeckConfig | None = await self._deck_config_gateway.read_by_id(
            DeckConfigID(source_deck.deck_config_id),
        )

        if source_config is None:
            msg = "Deck config not found"
            raise DeckConfigNotFoundError(msg)

        new_config: DeckConfig = self._deck_config_service.copy_config(
            config=source_config,
            new_owner_id=current_user.id,
        )

        new_deck: Deck = self._deck_service.copy_deck(
            deck=source_deck,
            new_user_id=current_user.id,
            new_deck_config_id=new_config.id,
            is_public=False,
        )

        source_cards: list[Card] = await self._card_gateway.read_all_by_deck(source_deck.id)

        await self._deck_config_gateway.add(new_config)
        await self._deck_gateway.add(new_deck)

        for card in source_cards:
            new_card: Card = self._card_service.copy_card(card=card, new_deck_id=new_deck.id)
            await self._card_gateway.add(new_card)

        await self._transaction_manager.commit()

        return CopyDeckView(
            deck_id=new_deck.id,
            deck_config_id=new_config.id,
        )
