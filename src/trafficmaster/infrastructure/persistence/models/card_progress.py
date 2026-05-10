import sqlalchemy as sa
from sqlalchemy.orm import composite

from trafficmaster.domain.card_progress.entities.card_progress import CardProgress
from trafficmaster.domain.card_progress.values.card_state import CardState
from trafficmaster.domain.card_progress.values.ease_factor import EaseFactor
from trafficmaster.domain.card_progress.values.interval import Interval
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

card_progress_table = sa.Table(
    "card_progress",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("card_id", sa.UUID(as_uuid=True), sa.ForeignKey("cards.id"), nullable=False),
    sa.Column("ease_factor", sa.Float, nullable=False),
    sa.Column("interval", sa.Integer, nullable=False),
    sa.Column("repetitions", sa.Integer, nullable=False, default=0),
    sa.Column("state", sa.Enum(CardState), nullable=False),
    sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
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
    sa.UniqueConstraint("user_id", "card_id", name="uq_card_progress_user_id_card_id"),
)


def map_card_progress_table() -> None:
    mapper_registry.map_imperatively(
        CardProgress,
        card_progress_table,
        properties={
            "id": card_progress_table.c.id,
            "user_id": card_progress_table.c.user_id,
            "card_id": card_progress_table.c.card_id,
            "ease_factor": composite(EaseFactor, card_progress_table.c.ease_factor),
            "interval": composite(Interval, card_progress_table.c.interval),
            "repetitions": card_progress_table.c.repetitions,
            "state": card_progress_table.c.state,
            "next_review_at": card_progress_table.c.next_review_at,
            "created_at": card_progress_table.c.created_at,
            "updated_at": card_progress_table.c.updated_at,
        },
    )
