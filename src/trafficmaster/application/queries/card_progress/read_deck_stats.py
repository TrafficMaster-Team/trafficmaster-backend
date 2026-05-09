from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.clock import Clock
from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.card_progress.read_deck_stats import ReadDeckStatsView
from trafficmaster.application.errors.deck import DeckConfigNotFoundError, DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadDeckStatsQuery:
    deck_id: UUID


class ReadDeckStatsQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
        access_service: AccessService,
        deck_config_gateway: DeckConfigGateway,
        card_gateway: CardGateway,
        card_progress_gateway: CardProgressGateway,
        review_log_gateway: ReviewLogGateway,
        clock: Clock,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_service: Final[AccessService] = access_service
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._card_gateway: Final[CardGateway] = card_gateway
        self._card_progress_gateway: Final[CardProgressGateway] = card_progress_gateway
        self._review_log_gateway: Final[ReviewLogGateway] = review_log_gateway
        self._clock: Final[Clock] = clock

    async def __call__(self, data: ReadDeckStatsQuery) -> ReadDeckStatsView:
        now = self._clock.current_time
        today_start = self._clock.today_start

        current_user: User = await self._current_user_service.get_current_user()

        deck: Deck | None = await self._deck_gateway.read_deck_by_id(DeckID(data.deck_id))

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
            msg = "You don't have access to this deck"
            raise NoPermissionToManageUserError(msg)

        deck_config: DeckConfig | None = await self._deck_config_gateway.read_by_id(
            DeckConfigID(deck.deck_config_id),
        )

        if deck_config is None:
            msg = "Deck config not found"
            raise DeckConfigNotFoundError(msg)

        total_cards: int = await self._card_gateway.count_by_deck(deck.id)

        state_counts: dict[CardState | None, int] = await self._card_progress_gateway.count_by_state(
            user_id=current_user.id,
            deck_id=deck.id,
        )
        learning_count: int = state_counts.get(CardState.LEARNING, 0) + state_counts.get(CardState.RELEARNING, 0)
        review_count: int = state_counts.get(CardState.REVIEW, 0)
        new_count: int = max(0, total_cards - learning_count - review_count)

        due_learning: int = await self._card_progress_gateway.count_due_learning(
            user_id=current_user.id,
            deck_id=deck.id,
            now=now,
        )
        due_review: int = await self._card_progress_gateway.count_due_review(
            user_id=current_user.id,
            deck_id=deck.id,
            now=now,
        )

        new_done_today: int = await self._review_log_gateway.read_count_new_done(
            user_id=current_user.id,
            deck_id=deck.id,
            since=today_start,
        )
        reviews_done_today: int = await self._review_log_gateway.read_count_reviews_done(
            user_id=current_user.id,
            deck_id=deck.id,
            since=today_start,
        )

        new_quota_left: int = max(0, deck_config.daily_limits.new_cards_per_day - new_done_today)
        new_available: int = min(new_count, new_quota_left)

        return ReadDeckStatsView(
            total_cards=total_cards,
            new_count=new_count,
            learning_count=learning_count,
            review_count=review_count,
            due_learning=due_learning,
            due_review=due_review,
            new_available=new_available,
            new_done_today=new_done_today,
            reviews_done_today=reviews_done_today,
        )
