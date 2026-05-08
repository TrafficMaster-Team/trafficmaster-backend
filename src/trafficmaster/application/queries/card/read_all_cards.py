from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.query_params.card_filters import CardParams, CardQueryFilters
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.common.query_params.sorting import SortingOrder
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.card.read_by_id import ReadCardByIDView
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.query_params import SortingError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadAllCardsQuery:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder
    deck_id: UUID
    tags: list[str] | None = None


class ReadAllCardsQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        card_gateway: CardGateway,
        access_service: AccessService,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
    ) -> None:
        self._access_service: Final[AccessService] = access_service
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._card_gateway: Final[CardGateway] = card_gateway
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway

    async def __call__(self, data: ReadAllCardsQuery) -> list[ReadCardByIDView]:

        current_user: User = await self._current_user_service.get_current_user()

        deck: Deck | None = await self._deck_gateway.read_deck_by_id(DeckID(data.deck_id))

        if deck is None:
            msg = "Deck not found"
            raise DeckNotFoundError(msg)

        user: User | None = await self._user_gateway.read_by_id(UserID(deck.owner_id))

        if user is None:
            msg = "User not found"
            raise UserNotFoundByIdError(msg)

        if not self._access_service.can_manage_user(subject=current_user, target=user):
            msg = "You don't have permission to do that"
            raise NoPermissionToManageUserError(msg)

        cards: list[Card] | None = await self._card_gateway.read_all_deck_cards(
            deck_id=deck.id,
            card_params=CardParams(
                pagination=Pagination(
                    limit=data.limit,
                    offset=data.offset,
                ),
                sorting_filter=CardQueryFilters(data.sorting_field),
                sorting_order=data.sorting_order,
                deck_id=deck.id,
                tags=tuple(data.tags) if data.tags is not None else None,
            ),
        )

        if cards is None:
            msg = "Invalid sorting parameters."
            raise SortingError(msg)

        return [
            ReadCardByIDView(
                id=card.id,
                question=str(card.question),
                answer=str(card.answer),
                deck_id=card.deck_id,
                tags=list(map(str, card.tags)),
                image_path=card.image_path,
            )
            for card in cards
        ]
