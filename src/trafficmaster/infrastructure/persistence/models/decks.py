import sqlalchemy as sa
from sqlalchemy.orm import composite

from trafficmaster.domain.deck.entities.deck import Deck
from trafficmaster.domain.deck.values.deck_title import DeckTitle
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

decks_table = sa.Table(
    "decks",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("owner_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("deck_config_id", sa.UUID(as_uuid=True), sa.ForeignKey("deck_configs.id"), nullable=False),
    sa.Column("title", sa.String(length=100), nullable=False),
    sa.Column("description", sa.String(length=1000), nullable=True),
    sa.Column("is_public", sa.Boolean, nullable=False, default=False),
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


def map_decks_table() -> None:
    mapper_registry.map_imperatively(
        Deck,
        decks_table,
        properties={
            "id": decks_table.c.id,
            "owner_id": decks_table.c.owner_id,
            "deck_config_id": decks_table.c.deck_config_id,
            "title": composite(DeckTitle, decks_table.c.title),
            "description": decks_table.c.description,
            "is_public": decks_table.c.is_public,
            "created_at": decks_table.c.created_at,
            "updated_at": decks_table.c.updated_at,
        },
    )
