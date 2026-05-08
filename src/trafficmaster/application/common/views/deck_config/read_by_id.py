from dataclasses import dataclass
from uuid import UUID

from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig


@dataclass(frozen=True, slots=True, kw_only=True)
class ReadDeckConfigByIDView:
    id: UUID
    owner_id: UUID
    name: str
    daily_limits: DailyLimits
    new_cards: NewCardsConfig
    lapses: LapsesConfig
    advanced: AdvancedConfig
