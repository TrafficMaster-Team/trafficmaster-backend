from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.deck.read_by_id import ReadDeckByIDView
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadDecksByUserIdQuery:
    user_id: UUID


class ReadDecksByUserIdQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        access_service: AccessService,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway

    async def __call__(self, data: ReadDecksByUserIdQuery) -> list[ReadDeckByIDView]:

        current_user: User = await self._current_user_service.get_current_user()

        user: User | None = await self._user_gateway.read_by_id(UserID(data.user_id))

        if user is None:
            msg = f"Can't find user with id {data.user_id}"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        decks: list[Deck] | None = await self._deck_gateway.read_decks_by_user_id(UserID(data.user_id))

        if decks is None:
            return []

        return [
            ReadDeckByIDView(
                id=deck.id,
                owner_id=deck.owner_id,
                deck_config_id=deck.deck_config_id,
                title=str(deck.title),
                description=deck.description,
                is_public=deck.is_public,
            )
            for deck in decks
        ]
