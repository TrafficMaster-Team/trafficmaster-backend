from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.deck_config.create_deck_config import CreateDeckConfigView
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.deck.services.deck_config_service import DeckConfigService
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDeckConfigCommand:
    owner_id: UUID
    name: str
    daily_limits: DailyLimits
    new_cards: NewCardsConfig
    lapses: LapsesConfig
    advanced: AdvancedConfig


class CreateDeckConfigCommandHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_gateway: UserGateway,
        access_service: AccessService,
        transaction_manager: TransactionManager,
        deck_config_gateway: DeckConfigGateway,
        deck_config_service: DeckConfigService,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_service: Final[AccessService] = access_service
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._deck_config_service: Final[DeckConfigService] = deck_config_service

    async def __call__(self, data: CreateDeckConfigCommand) -> CreateDeckConfigView:

        current_user: User = await self._current_user_service.get_current_user()

        user: User | None = await self._user_gateway.read_by_id(UserID(data.owner_id))

        if user is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You are not allowed to create a deck config for this user"
            raise NoPermissionToManageUserError(msg)

        created_deck_config: DeckConfig = self._deck_config_service.create_config(
            owner_id=user.id,
            name=DeckConfigName(data.name),
            daily_limits=data.daily_limits,
            new_cards=data.new_cards,
            lapses=data.lapses,
            advanced=data.advanced,
        )

        await self._deck_config_gateway.add(created_deck_config)
        await self._transaction_manager.commit()

        return CreateDeckConfigView(id=created_deck_config.id)
