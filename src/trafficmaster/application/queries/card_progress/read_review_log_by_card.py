from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.card_progress.review_log import ReviewLogView
from trafficmaster.application.errors.card import CardNotFoundError
from trafficmaster.application.errors.deck import DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.card.entities.card import Card
    from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadReviewLogByCardQuery:
    card_id: UUID
    limit: int | None = None
    offset: int | None = None


class ReadReviewLogByCardQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        card_gateway: CardGateway,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
        review_log_gateway: ReviewLogGateway,
        access_service: AccessService,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._card_gateway: Final[CardGateway] = card_gateway
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._review_log_gateway: Final[ReviewLogGateway] = review_log_gateway
        self._access_service: Final[AccessService] = access_service

    async def __call__(self, data: ReadReviewLogByCardQuery) -> list[ReviewLogView]:
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

        logs: list[ReviewLog] = await self._review_log_gateway.read_by_card(
            user_id=current_user.id,
            card_id=card.id,
            pagination=Pagination(limit=data.limit, offset=data.offset),
        )

        return [
            ReviewLogView(
                id=log.id,
                user_id=log.user_id,
                card_id=log.card_id,
                rating=log.rating,
                reviewed_at=log.reviewed_at,
            )
            for log in logs
        ]
