from dataclasses import dataclass
from datetime import UTC, datetime

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.errors.deck_config import MinIntervalGreaterThanMaxIntervalError
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig
from trafficmaster.domain.user.values.user_id import UserID


@dataclass(eq=False)
class DeckConfig(BaseEntity[DeckConfigID]):
    """
    SRS configuration for a deck.
    params:
        owner_id: id of the user who owns this config,
        name: display name of the configuration,
        daily_limits: limits on new cards and reviews per day,
        new_cards: learning steps and graduation intervals for new cards,
        lapses: relearning steps and minimum interval for forgotten cards,
        advanced: ease factor, interval modifiers and other SRS tuning.
    """

    owner_id: UserID
    name: DeckConfigName
    daily_limits: DailyLimits
    new_cards: NewCardsConfig
    lapses: LapsesConfig
    advanced: AdvancedConfig

    def __post_init__(self) -> None:
        super().__post_init__()
        self._validate_interval_bounds(lapses=self.lapses, advanced=self.advanced)

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
        self._validate_interval_bounds(lapses=lapses, advanced=self.advanced)
        self.lapses = lapses
        self.updated_at = datetime.now(UTC)

    def change_advanced(self, advanced: AdvancedConfig) -> None:
        self._validate_interval_bounds(lapses=self.lapses, advanced=advanced)
        self.advanced = advanced
        self.updated_at = datetime.now(UTC)

    @staticmethod
    def _validate_interval_bounds(*, lapses: LapsesConfig, advanced: AdvancedConfig) -> None:
        if lapses.min_interval > advanced.max_interval:
            msg = "Minimum lapse interval cannot be greater than maximum review interval"
            raise MinIntervalGreaterThanMaxIntervalError(msg)
