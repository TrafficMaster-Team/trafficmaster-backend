import sqlalchemy as sa
from sqlalchemy.orm import composite

from trafficmaster.domain.deck.entities.deck_config import DeckConfig
from trafficmaster.domain.deck.values.advanced_config import AdvancedConfig
from trafficmaster.domain.deck.values.daily_limits import DailyLimits
from trafficmaster.domain.deck.values.deck_config_name import DeckConfigName
from trafficmaster.domain.deck.values.lapses_config import LapsesConfig, LeechAction
from trafficmaster.domain.deck.values.new_cards_config import NewCardOrder, NewCardsConfig
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

deck_configs_table = sa.Table(
    "deck_configs",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("owner_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("name", sa.String(length=100), nullable=False),
    sa.Column("new_cards_per_day", sa.Integer, nullable=False),
    sa.Column("max_reviews_per_day", sa.Integer, nullable=False),
    sa.Column("reviews_dont_bury_new", sa.Boolean, nullable=False),
    sa.Column("learning_steps", sa.ARRAY(sa.Integer), nullable=False),
    sa.Column("graduating_interval", sa.Integer, nullable=False),
    sa.Column("easy_interval", sa.Integer, nullable=False),
    sa.Column("new_card_order", sa.Enum(NewCardOrder), nullable=False),
    sa.Column("relearning_steps", sa.ARRAY(sa.Integer), nullable=False),
    sa.Column("min_interval", sa.Integer, nullable=False),
    sa.Column("leech_threshold", sa.Integer, nullable=False),
    sa.Column("leech_action", sa.Enum(LeechAction), nullable=False),
    sa.Column("max_interval", sa.Integer, nullable=False),
    sa.Column("ease_factor", sa.Float, nullable=False),
    sa.Column("easy_factor", sa.Float, nullable=False),
    sa.Column("interval_modifier", sa.Float, nullable=False),
    sa.Column("hard_interval", sa.Float, nullable=False),
    sa.Column("new_interval", sa.Float, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


def map_deck_configs_table() -> None:
    mapper_registry.map_imperatively(
        DeckConfig,
        deck_configs_table,
        properties={
            "id": deck_configs_table.c.id,
            "owner_id": deck_configs_table.c.owner_id,
            "name": composite(DeckConfigName, deck_configs_table.c.name),
            "daily_limits": composite(
                DailyLimits,
                deck_configs_table.c.new_cards_per_day,
                deck_configs_table.c.max_reviews_per_day,
                deck_configs_table.c.reviews_dont_bury_new,
            ),
            "new_cards": composite(
                NewCardsConfig,
                deck_configs_table.c.learning_steps,
                deck_configs_table.c.graduating_interval,
                deck_configs_table.c.easy_interval,
                deck_configs_table.c.new_card_order,
            ),
            "lapses": composite(
                LapsesConfig,
                deck_configs_table.c.relearning_steps,
                deck_configs_table.c.min_interval,
                deck_configs_table.c.leech_threshold,
                deck_configs_table.c.leech_action,
            ),
            "advanced": composite(
                AdvancedConfig,
                deck_configs_table.c.max_interval,
                deck_configs_table.c.ease_factor,
                deck_configs_table.c.easy_factor,
                deck_configs_table.c.interval_modifier,
                deck_configs_table.c.hard_interval,
                deck_configs_table.c.new_interval,
            ),
            "created_at": deck_configs_table.c.created_at,
            "updated_at": deck_configs_table.c.updated_at,
        },
    )
