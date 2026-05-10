import sqlalchemy as sa

from trafficmaster.domain.card_progress.entities.review_log import ReviewLog
from trafficmaster.domain.card_progress.values.review_rating import ReviewRating
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

review_logs_table = sa.Table(
    "review_logs",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("card_id", sa.UUID(as_uuid=True), sa.ForeignKey("cards.id"), nullable=False),
    sa.Column("rating", sa.Enum(ReviewRating), nullable=False),
    sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
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
    sa.Index("ix_review_logs_user_id_reviewed_at", "user_id", "reviewed_at"),
    sa.Index("ix_review_logs_card_id_reviewed_at", "card_id", "reviewed_at"),
)


def map_review_logs_table() -> None:
    mapper_registry.map_imperatively(
        ReviewLog,
        review_logs_table,
        properties={
            "id": review_logs_table.c.id,
            "user_id": review_logs_table.c.user_id,
            "card_id": review_logs_table.c.card_id,
            "rating": review_logs_table.c.rating,
            "reviewed_at": review_logs_table.c.reviewed_at,
            "created_at": review_logs_table.c.created_at,
            "updated_at": review_logs_table.c.updated_at,
        },
    )
