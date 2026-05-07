from typing import Final

from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.ports.deck_config_id_generator import DeckConfigIDGenerator
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig
from trafficmaster.domain.user.values.user_id import UserID


class DeckConfigService:
    def __init__(self, id_generator: DeckConfigIDGenerator) -> None:
        self._id_generator: Final[DeckConfigIDGenerator] = id_generator

    def create_config(
        self,
        owner_id: UserID,
        name: DeckConfigName,
        daily_limits: DailyLimits,
        new_cards: NewCardsConfig,
        lapses: LapsesConfig,
        advanced: AdvancedConfig,
    ) -> DeckConfig:

        config_id = self._id_generator()
        return DeckConfig(
            id=config_id,
            owner_id=owner_id,
            name=name,
            daily_limits=daily_limits,
            new_cards=new_cards,
            lapses=lapses,
            advanced=advanced,
        )
