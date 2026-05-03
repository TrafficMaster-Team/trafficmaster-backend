from datetime import UTC, datetime, timedelta
from typing import Final

from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.ports.card_progress_id_generator import CardProgressIdGenerator
from trafficmaster.domain.card_progress.ports.review_id_generator import ReviewIdGenerator
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.interval import Interval
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig
from trafficmaster.domain.user.values.user_id import UserID

_MIN_EASE_FACTOR = 1.3
_EASE_AGAIN_PENALTY = 0.2
_EASE_HARD_PENALTY = 0.15
_EASE_EASY_BONUS = 0.15


class CardProgressService:
    def __init__(
        self,
        card_progress_id_generator: CardProgressIdGenerator,
        review_id_generator: ReviewIdGenerator,
    ) -> None:
        self.card_progress_id_generator: Final[CardProgressIdGenerator] = card_progress_id_generator
        self.review_id_generator: Final[ReviewIdGenerator] = review_id_generator

    def create_card_progress(
        self,
        user_id: UserID,
        card_id: CardID,
        default_ease_factor: EaseFactor,
    ) -> CardProgress:
        return CardProgress(
            id=self.card_progress_id_generator(),
            user_id=user_id,
            card_id=card_id,
            ease_factor=default_ease_factor,
            interval=Interval(1),
            repetitions=0,
            state=CardState.NEW,
            next_review_at=None,
        )

    def learning_process(
        self,
        progress: CardProgress,
        rating: ReviewRating,
        config: NewCardsConfig,
    ) -> ReviewLog:
        now = datetime.now(UTC)
        steps = config.learning_steps
        progress.state = CardState.LEARNING

        match rating:
            case ReviewRating.AGAIN:
                progress.repetitions = 0
                progress.next_review_at = now + timedelta(minutes=steps[0])

            case ReviewRating.HARD:
                progress.next_review_at = now + timedelta(minutes=steps[progress.repetitions])

            case ReviewRating.GOOD:
                next_step = progress.repetitions + 1
                if next_step >= len(steps):
                    progress.state = CardState.REVIEW
                    progress.interval = Interval(config.graduating_interval)
                    progress.repetitions = 1
                    progress.next_review_at = now + timedelta(days=config.graduating_interval)
                else:
                    progress.repetitions = next_step
                    progress.next_review_at = now + timedelta(minutes=steps[next_step])

            case ReviewRating.EASY:
                progress.state = CardState.REVIEW
                progress.interval = Interval(config.easy_interval)
                progress.repetitions = 1
                progress.next_review_at = now + timedelta(days=config.easy_interval)

        progress.updated_at = now

        return ReviewLog(
            id=self.review_id_generator(),
            user_id=progress.user_id,
            card_id=progress.card_id,
            rating=rating,
            reviewed_at=now,
        )

    def review_process(
        self,
        progress: CardProgress,
        rating: ReviewRating,
        config: AdvancedConfig,
    ) -> ReviewLog:
        now = datetime.now(UTC)
        current_ease = progress.ease_factor.value
        delay = max(0, (now - progress.next_review_at).days) if progress.next_review_at else 0
        current_interval = progress.interval.value + delay

        match rating:
            case ReviewRating.AGAIN:
                new_ease = max(_MIN_EASE_FACTOR, current_ease - _EASE_AGAIN_PENALTY)
                new_interval = max(1, round(current_interval * config.new_interval))
                progress.ease_factor = EaseFactor(new_ease)
                progress.interval = Interval(new_interval)
                progress.repetitions = 0
                progress.state = CardState.RELEARNING
                progress.next_review_at = now + timedelta(days=new_interval)

            case ReviewRating.HARD:
                new_ease = max(_MIN_EASE_FACTOR, current_ease - _EASE_HARD_PENALTY)
                new_interval = max(
                    current_interval + 1, round(current_interval * config.hard_interval * config.interval_modificator)
                )
                new_interval = min(new_interval, config.max_interval)
                progress.ease_factor = EaseFactor(new_ease)
                progress.interval = Interval(new_interval)
                progress.repetitions += 1
                progress.next_review_at = now + timedelta(days=new_interval)

            case ReviewRating.GOOD:
                new_interval = max(
                    current_interval + 1, round(current_interval * current_ease * config.interval_modificator)
                )
                new_interval = min(new_interval, config.max_interval)
                progress.interval = Interval(new_interval)
                progress.repetitions += 1
                progress.next_review_at = now + timedelta(days=new_interval)

            case ReviewRating.EASY:
                new_ease = current_ease + _EASE_EASY_BONUS
                new_interval = max(
                    current_interval + 1,
                    round(current_interval * new_ease * config.interval_modificator * config.easy_factor),
                )
                new_interval = min(new_interval, config.max_interval)
                progress.ease_factor = EaseFactor(new_ease)
                progress.interval = Interval(new_interval)
                progress.repetitions += 1
                progress.next_review_at = now + timedelta(days=new_interval)

        progress.updated_at = now

        return ReviewLog(
            id=self.review_id_generator(),
            user_id=progress.user_id,
            card_id=progress.card_id,
            rating=rating,
            reviewed_at=now,
        )

    def relearning_process(
        self,
        progress: CardProgress,
        rating: ReviewRating,
        config: LapsesConfig,
    ) -> ReviewLog:
        now = datetime.now(UTC)
        steps = config.relearning_steps

        match rating:
            case ReviewRating.AGAIN:
                progress.repetitions = 0
                progress.next_review_at = now + timedelta(minutes=steps[0])

            case ReviewRating.HARD:
                progress.next_review_at = now + timedelta(minutes=steps[progress.repetitions])

            case ReviewRating.GOOD:
                next_step = progress.repetitions + 1
                if next_step >= len(steps):
                    progress.state = CardState.REVIEW
                    progress.interval = Interval(max(config.min_interval, progress.interval.value))
                    progress.repetitions = 1
                    progress.next_review_at = now + timedelta(days=progress.interval.value)
                else:
                    progress.repetitions = next_step
                    progress.next_review_at = now + timedelta(minutes=steps[next_step])

            case ReviewRating.EASY:
                progress.state = CardState.REVIEW
                progress.interval = Interval(max(config.min_interval, progress.interval.value))
                progress.repetitions = 1
                progress.next_review_at = now + timedelta(days=progress.interval.value)

        progress.updated_at = now

        return ReviewLog(
            id=self.review_id_generator(),
            user_id=progress.user_id,
            card_id=progress.card_id,
            rating=rating,
            reviewed_at=now,
        )

    def schedule(
        self,
        progress: CardProgress,
        rating: ReviewRating,
        deck: DeckConfig,
    ) -> ReviewLog:
        match progress.state:
            case CardState.NEW | CardState.LEARNING:
                return self.learning_process(
                    progress=progress,
                    rating=rating,
                    config=deck.new_cards,
                )

            case CardState.REVIEW:
                return self.review_process(
                    progress=progress,
                    rating=rating,
                    config=deck.advanced,
                )

            case CardState.RELEARNING:
                return self.relearning_process(
                    progress=progress,
                    rating=rating,
                    config=deck.lapses,
                )
