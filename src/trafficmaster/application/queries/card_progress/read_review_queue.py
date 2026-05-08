from dataclasses import dataclass
from typing import TYPE_CHECKING, Final
from uuid import UUID

from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.card_with_progress import CardWithProgress
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.clock import Clock
from trafficmaster.application.common.ports.deck.deck_config_gateway import DeckConfigGateway
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.ports.user.user_gateway import UserGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.card_progress.review_queue_item import (
    ReviewQueueItemView,
    ReviewReason,
)
from trafficmaster.application.errors.deck import DeckConfigNotFoundError, DeckNotFoundError
from trafficmaster.application.errors.user import NoPermissionToManageUserError, UserNotFoundByIdError
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.user.services.access_service import AccessService
from trafficmaster.domain.user.values.user_id import UserID

if TYPE_CHECKING:
    from trafficmaster.domain.deck.entities.deck import Deck
    from trafficmaster.domain.deck.entities.deck_config import DeckConfig
    from trafficmaster.domain.user.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadReviewQueueQuery:
    deck_id: UUID
    limit: int


class ReadReviewQueueQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        deck_gateway: DeckGateway,
        user_gateway: UserGateway,
        access_service: AccessService,
        deck_config_gateway: DeckConfigGateway,
        card_progress_gateway: CardProgressGateway,
        review_log_gateway: ReviewLogGateway,
        clock: Clock,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._user_gateway: Final[UserGateway] = user_gateway
        self._access_service: Final[AccessService] = access_service
        self._deck_config_gateway: Final[DeckConfigGateway] = deck_config_gateway
        self._card_progress_gateway: Final[CardProgressGateway] = card_progress_gateway
        self._review_log_gateway: Final[ReviewLogGateway] = review_log_gateway
        self._clock: Final[Clock] = clock

    async def __call__(self, data: ReadReviewQueueQuery) -> list[ReviewQueueItemView]:

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

        queue: list[ReviewQueueItemView] = []
        remaining: int = data.limit

        learning: list[CardWithProgress] = await self._card_progress_gateway.read_due_learning(
            user_id=current_user.id,
            deck_id=deck.id,
            now=now,
            limit=remaining,
        )
        queue.extend(self._to_view(row, ReviewReason.LEARNING) for row in learning)
        remaining = max(0, remaining - len(learning))

        if remaining > 0:
            reviews_done_today = await self._review_log_gateway.read_count_reviews_done(
                user_id=current_user.id,
                deck_id=deck.id,
                since=today_start,
            )
            review_left = max(0, deck_config.daily_limits.max_reviews_per_day - reviews_done_today)
            review: list[CardWithProgress] = await self._card_progress_gateway.read_due_review(
                user_id=current_user.id,
                deck_id=deck.id,
                now=now,
                limit=min(remaining, review_left),
            )
            queue.extend(self._to_view(row, ReviewReason.REVIEW) for row in review)
            remaining = max(0, remaining - len(review))

        if remaining > 0:
            new_done_today = await self._review_log_gateway.read_count_new_done(
                user_id=current_user.id,
                deck_id=deck.id,
                since=today_start,
            )
            new_left = max(0, deck_config.daily_limits.new_cards_per_day - new_done_today)
            new_cards: list[CardWithProgress] = await self._card_progress_gateway.read_new_cards(
                user_id=current_user.id,
                deck_id=deck.id,
                now=now,
                limit=min(remaining, new_left),
                order=deck_config.new_cards.new_card_order,
            )
            queue.extend(self._to_view(row, ReviewReason.NEW) for row in new_cards)

        return queue

    @staticmethod
    def _to_view(row: CardWithProgress, reason: ReviewReason) -> ReviewQueueItemView:
        progress = row.progress
        return ReviewQueueItemView(
            card_id=row.card.id,
            question=str(row.card.question),
            answer=str(row.card.answer),
            image_path=row.card.image_path,
            tags=[str(tag) for tag in row.card.tags],
            state=progress.state if progress is not None else None,
            interval=progress.interval.value if progress is not None else None,
            repetitions=progress.repetitions if progress is not None else None,
            next_review_at=progress.next_review_at if progress is not None else None,
            reason=reason,
        )
