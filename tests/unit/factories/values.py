import uuid
from uuid import UUID

from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_id import CardID
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.domain.card_progress.values.card_progress_id import CardProgressID
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.interval import Interval
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.deck_id import DeckID
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig, LeechAction
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder, NewCardsConfig
from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.raw_password import RawPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_id import UserID
from trafficmaster.domain.user.values.user_name import Username
from trafficmaster.domain.user.values.user_role import UserRole


# --- User ---
def create_user_id(value: UUID | None = None) -> UserID:
    return UserID(value or uuid.uuid4())


def create_username(value: str = "Alice") -> Username:
    return Username(name=value)


def create_raw_password(value: str = "Good Password1") -> RawPassword:
    return RawPassword(value=value)


def create_password_hash(value: bytes = b"password_hash") -> HashedPassword:
    return HashedPassword(password=value)


def create_user_email(value: str = "alice@example.com") -> UserEmail:
    return UserEmail(email=value)


def create_user_role(value: UserRole = UserRole.USER) -> UserRole:
    return value


# --- Card ---
def create_card_id(value: UUID | None = None) -> CardID:
    return CardID(value or uuid.uuid4())


def create_card_question(value: str = "What is the capital of France?") -> CardQuestion:
    return CardQuestion(value=value)


def create_card_answer(value: str = "Paris") -> CardAnswer:
    return CardAnswer(value=value)


def create_card_tag(value: str = "geography") -> CardTag:
    return CardTag(value=value)


# --- Card progress ---
def create_card_progress_id(value: UUID | None = None) -> CardProgressID:
    return CardProgressID(value or uuid.uuid4())


def create_review_log_id(value: UUID | None = None) -> ReviewLogID:
    return ReviewLogID(value or uuid.uuid4())


def create_card_state(value: CardState = CardState.NEW) -> CardState:
    return value


def create_ease_factor(value: float = 2.5) -> EaseFactor:
    return EaseFactor(value=value)


def create_interval(value: int = 1) -> Interval:
    return Interval(value=value)


def create_review_rating(value: ReviewRating = ReviewRating.GOOD) -> ReviewRating:
    return value


# --- Deck ---
def create_deck_id(value: UUID | None = None) -> DeckID:
    return DeckID(value or uuid.uuid4())


def create_deck_title(value: str = "My Deck") -> DeckTitle:
    return DeckTitle(value=value)


# --- Deck config ---
def create_deck_config_id(value: UUID | None = None) -> DeckConfigID:
    return DeckConfigID(value or uuid.uuid4())


def create_deck_config_name(value: str = "Default") -> DeckConfigName:
    return DeckConfigName(value=value)


def create_daily_limits(
    new_cards_per_day: int = 20,
    max_reviews_per_day: int = 200,
    *,
    reviews_dont_bury_new: bool = False,
) -> DailyLimits:
    return DailyLimits(
        new_cards_per_day=new_cards_per_day,
        max_reviews_per_day=max_reviews_per_day,
        reviews_dont_bury_new=reviews_dont_bury_new,
    )


def create_new_cards_config(
    learning_steps: list[int] | None = None,
    graduating_interval: int = 1,
    easy_interval: int = 4,
    new_card_order: NewCardOrder = NewCardOrder.SEQUENTIAL,
) -> NewCardsConfig:
    return NewCardsConfig(
        learning_steps=learning_steps if learning_steps is not None else [1, 10],
        graduating_interval=graduating_interval,
        easy_interval=easy_interval,
        new_card_order=new_card_order,
    )


def create_lapses_config(
    relearning_steps: list[int] | None = None,
    min_interval: int = 1,
    leech_threshold: int = 8,
    leech_action: LeechAction = LeechAction.SUSPEND,
) -> LapsesConfig:
    return LapsesConfig(
        relearning_steps=relearning_steps if relearning_steps is not None else [10],
        min_interval=min_interval,
        leech_threshold=leech_threshold,
        leech_action=leech_action,
    )


def create_advanced_config(
    max_interval: int = 36500,
    ease_factor: float = 2.5,
    easy_factor: float = 1.3,
    interval_modifier: float = 1.0,
    hard_interval: float = 1.2,
    new_interval: float = 0.0,
) -> AdvancedConfig:
    return AdvancedConfig(
        max_interval=max_interval,
        ease_factor=ease_factor,
        easy_factor=easy_factor,
        interval_modifier=interval_modifier,
        hard_interval=hard_interval,
        new_interval=new_interval,
    )
