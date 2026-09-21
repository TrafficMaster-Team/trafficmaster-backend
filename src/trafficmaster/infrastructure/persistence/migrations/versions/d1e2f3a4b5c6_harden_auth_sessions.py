"""harden auth sessions

Revision ID: d1e2f3a4b5c6
Revises: b8f1c2d3e4a5
Create Date: 2026-09-21 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: str | Sequence[str] | None = "b8f1c2d3e4a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_AUTH_SESSION_USER_FK = "pg_auth_sessions_user_id_users"
_AUTH_SESSION_USER_INDEX = "ix_auth_sessions_user_id"


def upgrade() -> None:
    """Remove orphan sessions, then enforce and index their user relationship."""
    op.execute(
        sa.text(
            "DELETE FROM auth_sessions AS auth_session "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM users WHERE users.id = auth_session.user_id"
            ")"
        )
    )
    op.create_foreign_key(
        _AUTH_SESSION_USER_FK,
        "auth_sessions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(_AUTH_SESSION_USER_INDEX, "auth_sessions", ["user_id"], unique=False)


def downgrade() -> None:
    """Restore the former unconstrained auth-session schema."""
    op.drop_index(_AUTH_SESSION_USER_INDEX, table_name="auth_sessions")
    op.drop_constraint(_AUTH_SESSION_USER_FK, "auth_sessions", type_="foreignkey")
