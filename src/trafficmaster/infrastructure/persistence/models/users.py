import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import composite

from trafficmaster.domain.user.entities.user import User
from trafficmaster.domain.user.values.hashed_password import HashedPassword
from trafficmaster.domain.user.values.user_email import UserEmail
from trafficmaster.domain.user.values.user_role import UserRole
from trafficmaster.infrastructure.persistence.models.base import mapper_registry

users_table = sa.Table(
    "users",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("email", sa.String(length=50), nullable=False, unique=True),
    sa.Column("name", sa.String(length=20), nullable=False),
    sa.Column("hashed_password", sa.LargeBinary(), nullable=False),
    sa.Column("role", sa.Enum(UserRole), nullable=False),
    sa.Column("is_active", sa.Boolean, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
    ),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "id": users_table.c.id,
            "email": composite(UserEmail, users_table.c.email),
            "role": users_table.c.role,
            "is_active": users_table.c.is_active,
            "created_at": users_table.c.created_at,
            "updated_at": users_table.c.updated_at,
            "hashed_password": composite(HashedPassword, users_table.c.hashed_password),
        },
    )
