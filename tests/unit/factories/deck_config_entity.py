from tests.unit.factories.values import (
    create_advanced_config,
    create_daily_limits,
    create_deck_config_id,
    create_deck_config_name,
    create_lapses_config,
    create_new_cards_config,
    create_user_id,
)
from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_id import DeckConfigID
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig
from trafficmaster.domain.deck.values.new_cards_config import NewCardsConfig
from trafficmaster.domain.user.values.user_id import UserID


def create_deck_config(
    config_id: DeckConfigID | None = None,
    owner_id: UserID | None = None,
    name: DeckConfigName | None = None,
    daily_limits: DailyLimits | None = None,
    new_cards: NewCardsConfig | None = None,
    lapses: LapsesConfig | None = None,
    advanced: AdvancedConfig | None = None,
) -> DeckConfig:
    return DeckConfig(
        id=config_id or create_deck_config_id(),
        owner_id=owner_id or create_user_id(),
        name=name or create_deck_config_name(),
        daily_limits=daily_limits or create_daily_limits(),
        new_cards=new_cards or create_new_cards_config(),
        lapses=lapses or create_lapses_config(),
        advanced=advanced or create_advanced_config(),
    )
