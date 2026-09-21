from sqlalchemy import UUID, Column, DateTime, ForeignKey, Index, String, Table

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

auth_sessions_table = Table(
    "auth_sessions",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
    Index("ix_auth_sessions_user_id", "user_id"),
)


def map_auth_session_table() -> None:
    mapper_registry.map_imperatively(
        AuthSession,
        auth_sessions_table,
        properties={
            "id_": auth_sessions_table.c.id,
            "user_id": auth_sessions_table.c.user_id,
            "expiration": auth_sessions_table.c.expiration,
        },
    )
