from sqlalchemy import UUID, Column, DateTime, String, Table

from trafficmaster.application.auth.auth_model import AuthSession
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

auth_sessions_table = Table(
    "auth_sessions",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("expiration", DateTime, nullable=False),
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
