from dataclasses import dataclass
from datetime import UTC, datetime

from trafficmaster.domain.common.entities.base_entity import BaseEntity
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig
from trafficmaster.domain.user.values.user_id import UserID


@dataclass
class DeckConfig(BaseEntity[DeckConfigID]):
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
