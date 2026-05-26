from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self, TypedDict
from uuid import UUID

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig, LeechAction
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder, NewCardsConfig
from trafficmaster.domain.user.values.user_id import UserID


class SerializedDailyLimits(TypedDict):
    new_cards_per_day: int
    max_reviews_per_day: int
    reviews_dont_bury_new: bool


class SerializedNewCardsConfig(TypedDict):
    learning_steps: list[int]
    graduating_interval: int
    easy_interval: int
    new_card_order: str


class SerializedLapsesConfig(TypedDict):
    relearning_steps: list[int]
    min_interval: int
    leech_threshold: int
    leech_action: str


class SerializedAdvancedConfig(TypedDict):
    max_interval: int
    ease_factor: float
    easy_factor: float
    interval_modifier: float
    hard_interval: float
    new_interval: float


class SerializedDeckConfig(TypedDict):
    id: str
    owner_id: str
    name: str
    daily_limits: SerializedDailyLimits
    new_cards: SerializedNewCardsConfig
    lapses: SerializedLapsesConfig
    advanced: SerializedAdvancedConfig
    created_at: str
    updated_at: str


@dataclass(eq=False)
class DeckConfig(BaseEntity[DeckConfigID]):
    """
    SRS configuration for a deck.
    params:
        owner_id: id of the user who owns this config,
        name: display name of the configuration,
        daily_limits: limits on new cards and reviews per day,
        new_cards: learning steps and graduation intervals for new cards,
        lapses: relearning steps and leech settings for forgotten cards,
        advanced: ease factor, interval modifiers and other SRS tuning.
    """

    owner_id: UserID
    name: DeckConfigName
    daily_limits: DailyLimits
    new_cards: NewCardsConfig
    lapses: LapsesConfig
    advanced: AdvancedConfig

    def change_config_name(self, name: DeckConfigName) -> None:
        self.name = name
        self.updated_at = datetime.now(UTC)

    def change_daily_limits(self, daily_limits: DailyLimits) -> None:
        self.daily_limits = daily_limits
        self.updated_at = datetime.now(UTC)

    def change_new_cards(self, new_cards: NewCardsConfig) -> None:
        self.new_cards = new_cards
        self.updated_at = datetime.now(UTC)

    def change_lapses(self, lapses: LapsesConfig) -> None:
        self.lapses = lapses
        self.updated_at = datetime.now(UTC)

    def change_advanced(self, advanced: AdvancedConfig) -> None:
        self.advanced = advanced
        self.updated_at = datetime.now(UTC)

    def serialize(self) -> SerializedDeckConfig:
        return {
            "id": str(self.id),
            "owner_id": str(self.owner_id),
            "name": str(self.name),
            "daily_limits": {
                "new_cards_per_day": self.daily_limits.new_cards_per_day,
                "max_reviews_per_day": self.daily_limits.max_reviews_per_day,
                "reviews_dont_bury_new": self.daily_limits.reviews_dont_bury_new,
            },
            "new_cards": {
                "learning_steps": list(self.new_cards.learning_steps),
                "graduating_interval": self.new_cards.graduating_interval,
                "easy_interval": self.new_cards.easy_interval,
                "new_card_order": self.new_cards.new_card_order.value,
            },
            "lapses": {
                "relearning_steps": list(self.lapses.relearning_steps),
                "min_interval": self.lapses.min_interval,
                "leech_threshold": self.lapses.leech_threshold,
                "leech_action": self.lapses.leech_action.value,
            },
            "advanced": {
                "max_interval": self.advanced.max_interval,
                "ease_factor": self.advanced.ease_factor,
                "easy_factor": self.advanced.easy_factor,
                "interval_modifier": self.advanced.interval_modifier,
                "hard_interval": self.advanced.hard_interval,
                "new_interval": self.advanced.new_interval,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: SerializedDeckConfig) -> Self:
        return cls(
            id=DeckConfigID(UUID(data["id"])),
            owner_id=UserID(UUID(data["owner_id"])),
            name=DeckConfigName(data["name"]),
            daily_limits=DailyLimits(
                new_cards_per_day=data["daily_limits"]["new_cards_per_day"],
                max_reviews_per_day=data["daily_limits"]["max_reviews_per_day"],
                reviews_dont_bury_new=data["daily_limits"]["reviews_dont_bury_new"],
            ),
            new_cards=NewCardsConfig(
                learning_steps=list(data["new_cards"]["learning_steps"]),
                graduating_interval=data["new_cards"]["graduating_interval"],
                easy_interval=data["new_cards"]["easy_interval"],
                new_card_order=NewCardOrder(data["new_cards"]["new_card_order"]),
            ),
            lapses=LapsesConfig(
                relearning_steps=list(data["lapses"]["relearning_steps"]),
                min_interval=data["lapses"]["min_interval"],
                leech_threshold=data["lapses"]["leech_threshold"],
                leech_action=LeechAction(data["lapses"]["leech_action"]),
            ),
            advanced=AdvancedConfig(
                max_interval=data["advanced"]["max_interval"],
                ease_factor=data["advanced"]["ease_factor"],
                easy_factor=data["advanced"]["easy_factor"],
                interval_modifier=data["advanced"]["interval_modifier"],
                hard_interval=data["advanced"]["hard_interval"],
                new_interval=data["advanced"]["new_interval"],
            ),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
