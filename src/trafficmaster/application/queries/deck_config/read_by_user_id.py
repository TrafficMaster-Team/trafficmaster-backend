from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.deck_config.read_by_id import ReadDeckConfigByIDView
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadDeckConfigsByUserIdQuery:
    user_id: UUID


class ReadDeckConfigsByUserIdQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        access_service: AccessService,
        deck_config_gateway: DeckConfigGateway,
        user_gateway: UserGateway,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._user_gateway: Final[UserGateway] = user_gateway

    async def __call__(self, data: ReadDeckConfigsByUserIdQuery) -> list[ReadDeckConfigByIDView]:

        current_user: User = await self._current_user_service.get_current_user()

        user: User | None = await self._user_gateway.read_by_id(UserID(data.user_id))

        if user is None:
            msg = f"Can't find user with id {data.user_id}"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        deck_configs: list[DeckConfig] = await self._deck_config_gateway.read_by_user_id(
            UserID(data.user_id),
        )

        return [
            ReadDeckConfigByIDView(
                id=deck_config.id,
                owner_id=deck_config.owner_id,
                name=str(deck_config.name),
                daily_limits=deck_config.daily_limits,
                new_cards=deck_config.new_cards,
                lapses=deck_config.lapses,
                advanced=deck_config.advanced,
            )
            for deck_config in deck_configs
        ]
