from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.transaction_manager import TransactionManager
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.errors.deck import DeckConfigNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeAdvancedCommand:
    deck_config_id: UUID
    advanced: AdvancedConfig


class ChangeAdvancedCommandHandler:
    def __init__(
        self,
        deck_config_gateway: DeckConfigGateway,
        user_gateway: UserGateway,
        transaction_manager: TransactionManager,
        current_user_service: CurrentUserService,
        access_service: AccessService,
    ) -> None:
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service

    async def __call__(self, data: ChangeAdvancedCommand) -> None:

        current_user: User = await self._current_user_service.get_current_user()

        deck_config: DeckConfig | None = await self._deck_config_gateway.read_by_id(
            DeckConfigID(data.deck_config_id),
        )

        if deck_config is None:
            msg = "Deck config not found"
            raise DeckConfigNotFoundError(msg)

        user: User | None = await self._user_gateway.read_by_id(UserID(deck_config.owner_id))

        if user is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You are not allowed to manage this deck config"
            raise NoPermissionToManageUserError(msg)

        deck_config.change_advanced(data.advanced)

        await self._transaction_manager.commit()
