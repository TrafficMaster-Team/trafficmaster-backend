from functools import lru_cache

from trafficmaster.infrastructure.persistence.models.auth_sessions import map_auth_session_table
from trafficmaster.infrastructure.persistence.models.card_progress import map_card_progress_table
from trafficmaster.infrastructure.persistence.models.cards import map_cards_table
from trafficmaster.infrastructure.persistence.models.deck_configs import map_deck_configs_table
from trafficmaster.infrastructure.persistence.models.decks import map_decks_table
from trafficmaster.infrastructure.persistence.models.review_logs import map_review_logs_table
from trafficmaster.infrastructure.persistence.models.users import map_users_table
from trafficmaster.setup.config.settings import AppConfig


@lru_cache(maxsize=1)
def setup_config() -> AppConfig:
    return AppConfig()


def setup_map_configs() -> None:
    map_auth_session_table()
    map_card_progress_table()
    map_cards_table()
    map_decks_table()
    map_deck_configs_table()
    map_review_logs_table()
    map_users_table()
