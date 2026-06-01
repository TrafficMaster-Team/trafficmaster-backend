from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import composite

from trafficmaster.domain.card.entities.card import Card
from trafficmaster.domain.card.values.card_answer import CardAnswer
from trafficmaster.domain.card.values.card_question import CardQuestion
from trafficmaster.domain.card.values.card_tag import CardTag
from trafficmaster.infrastructure.persistence.models.base import mapper_registry


class CardTagType(sa.types.TypeDecorator[CardTag]):
    """Bridges the ``CardTag`` value object to a plain string array element."""

    impl = sa.String
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:  # noqa: ANN401, ARG002
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value: Any, dialect: Any) -> CardTag | None:  # noqa: ANN401, ARG002
        if value is None:
            return None
        return CardTag(value)


cards_table = sa.Table(
    "cards",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("name", sa.String(length=100)),
    sa.Column("deck_id", sa.UUID(as_uuid=True), sa.ForeignKey("decks.id", ondelete="CASCADE"), nullable=False),
    sa.Column("question", sa.String(length=5000), key="card_question", nullable=False),
    sa.Column("answer", sa.String(length=5000), key="card_answer", nullable=False),
    sa.Column("image_path", sa.String, nullable=True),
    sa.Column("tags", MutableList.as_mutable(sa.ARRAY(CardTagType)), nullable=True),
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


def map_cards_table() -> None:
    mapper_registry.map_imperatively(
        Card,
        cards_table,
        properties={
            "id": cards_table.c.id,
            "question": composite(CardQuestion, cards_table.c.card_question),
            "answer": composite(CardAnswer, cards_table.c.card_answer),
            "image_path": cards_table.c.image_path,
            "tags": cards_table.c.tags,
            "created_at": cards_table.c.created_at,
            "updated_at": cards_table.c.updated_at,
            "deck_id": cards_table.c.deck_id,
        },
    )
