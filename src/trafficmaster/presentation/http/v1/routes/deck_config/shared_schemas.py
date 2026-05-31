from pydantic import BaseModel, ConfigDict, Field

from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig, LeechAction
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder, NewCardsConfig


class DailyLimitsSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    new_cards_per_day: int = Field(default=20, title="New cards per day", description="Daily limit of new cards")
    max_reviews_per_day: int = Field(default=200, title="Max reviews per day", description="Daily limit of reviews")
    reviews_dont_bury_new: bool = Field(
        default=False,
        title="Reviews don't bury new",
        description="Whether reviews do not bury sibling new cards",
    )

    def to_domain(self) -> DailyLimits:
        return DailyLimits(
            new_cards_per_day=self.new_cards_per_day,
            max_reviews_per_day=self.max_reviews_per_day,
            reviews_dont_bury_new=self.reviews_dont_bury_new,
        )


class NewCardsConfigSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    learning_steps: list[int] = Field(
        title="Learning steps", description="Learning steps in minutes", examples=[[1, 10]]
    )
    graduating_interval: int = Field(
        title="Graduating interval", description="Graduating interval in days", examples=[1]
    )
    easy_interval: int = Field(title="Easy interval", description="Easy interval in days", examples=[4])
    new_card_order: NewCardOrder = Field(title="New card order", description="Order new cards are introduced")

    def to_domain(self) -> NewCardsConfig:
        return NewCardsConfig(
            learning_steps=self.learning_steps,
            graduating_interval=self.graduating_interval,
            easy_interval=self.easy_interval,
            new_card_order=self.new_card_order,
        )


class LapsesConfigSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    relearning_steps: list[int] = Field(
        title="Relearning steps",
        description="Relearning steps in minutes",
        examples=[[10]],
    )
    min_interval: int = Field(title="Min interval", description="Minimum interval in days", examples=[1])
    leech_threshold: int = Field(
        title="Leech threshold", description="Lapses before a card becomes a leech", examples=[8]
    )
    leech_action: LeechAction = Field(title="Leech action", description="Action taken when a card becomes a leech")

    def to_domain(self) -> LapsesConfig:
        return LapsesConfig(
            relearning_steps=self.relearning_steps,
            min_interval=self.min_interval,
            leech_threshold=self.leech_threshold,
            leech_action=self.leech_action,
        )


class AdvancedConfigSchema(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    max_interval: int = Field(title="Max interval", description="Maximum interval in days", examples=[36500])
    ease_factor: float = Field(title="Ease factor", description="Starting ease factor", examples=[2.5])
    easy_factor: float = Field(title="Easy factor", description="Easy bonus factor", examples=[1.3])
    interval_modifier: float = Field(title="Interval modifier", description="Global interval modifier", examples=[1.0])
    hard_interval: float = Field(title="Hard interval", description="Hard interval factor", examples=[1.2])
    new_interval: float = Field(title="New interval", description="New interval factor after a lapse", examples=[0.0])

    def to_domain(self) -> AdvancedConfig:
        return AdvancedConfig(
            max_interval=self.max_interval,
            ease_factor=self.ease_factor,
            easy_factor=self.easy_factor,
            interval_modifier=self.interval_modifier,
            hard_interval=self.hard_interval,
            new_interval=self.new_interval,
        )
