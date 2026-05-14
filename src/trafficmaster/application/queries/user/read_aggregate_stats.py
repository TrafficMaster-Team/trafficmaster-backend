from typing import TYPE_CHECKING, Final

from trafficmaster.application.common.ports.card.card_gateway import CardGateway
from trafficmaster.application.common.ports.card_progress.card_progress_gateway import CardProgressGateway
from trafficmaster.application.common.ports.card_progress.review_log_gateway import ReviewLogGateway
from trafficmaster.application.common.ports.clock import Clock
from trafficmaster.application.common.ports.deck.deck_gateway import DeckGateway
from trafficmaster.application.common.services.current_user import CurrentUserService
from trafficmaster.application.common.views.user.aggregate_stats import UserAggregateStatsView
from trafficmaster.domain.card_progress.values.card_state import CardState

if TYPE_CHECKING:
    from trafficmaster.domain.user.entities.user import User


class ReadUserAggregateStatsQueryHandler:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        deck_gateway: DeckGateway,
        card_gateway: CardGateway,
        card_progress_gateway: CardProgressGateway,
        review_log_gateway: ReviewLogGateway,
        clock: Clock,
    ) -> None:
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._deck_gateway: Final[DeckGateway] = deck_gateway
        self._card_gateway: Final[CardGateway] = card_gateway
        self._card_progress_gateway: Final[CardProgressGateway] = card_progress_gateway
        self._review_log_gateway: Final[ReviewLogGateway] = review_log_gateway
        self._clock: Final[Clock] = clock

    async def __call__(self) -> UserAggregateStatsView:
        now = self._clock.current_time
        today_start = self._clock.today_start

        current_user: User = await self._current_user_service.get_current_user()

        total_decks: int = await self._deck_gateway.count_by_user(current_user.id)
        total_cards: int = await self._card_gateway.count_by_user(current_user.id)

        state_counts: dict[CardState | None, int] = await self._card_progress_gateway.count_by_state(
            user_id=current_user.id,
            deck_id=None,
        )
        learning_count: int = state_counts.get(CardState.LEARNING, 0) + state_counts.get(CardState.RELEARNING, 0)
        review_count: int = state_counts.get(CardState.REVIEW, 0)
        new_count: int = max(0, total_cards - learning_count - review_count)

        due_learning: int = await self._card_progress_gateway.count_due_learning(
            user_id=current_user.id,
            deck_id=None,
            now=now,
        )
        due_review: int = await self._card_progress_gateway.count_due_review(
            user_id=current_user.id,
            deck_id=None,
            now=now,
        )

        new_done_today: int = await self._review_log_gateway.count_new_done(
            user_id=current_user.id,
            deck_id=None,
            since=today_start,
        )
        reviews_done_today: int = await self._review_log_gateway.count_reviews_done(
            user_id=current_user.id,
            deck_id=None,
            since=today_start,
        )

        return UserAggregateStatsView(
            total_decks=total_decks,
            total_cards=total_cards,
            new_count=new_count,
            learning_count=learning_count,
            review_count=review_count,
            due_learning=due_learning,
            due_review=due_review,
            new_done_today=new_done_today,
            reviews_done_today=reviews_done_today,
        )
