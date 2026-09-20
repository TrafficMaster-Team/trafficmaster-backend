"""remove unused srs settings

Revision ID: b8f1c2d3e4a5
Revises: 39bef0dd9a44
Create Date: 2026-09-17 19:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b8f1c2d3e4a5"
down_revision: str | Sequence[str] | None = "39bef0dd9a44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_LEECH_ACTION_ENUM = postgresql.ENUM("TAG_ONLY", "SUSPEND", name="leechaction", create_type=False)


def upgrade() -> None:
    """Remove settings that have no corresponding scheduling behavior."""
    op.drop_column("deck_configs", "reviews_dont_bury_new")
    op.drop_column("deck_configs", "leech_threshold")
    op.drop_column("deck_configs", "leech_action")
    _LEECH_ACTION_ENUM.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Restore removed settings with their former defaults."""
    _LEECH_ACTION_ENUM.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "deck_configs",
        sa.Column("reviews_dont_bury_new", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "deck_configs",
        sa.Column("leech_threshold", sa.Integer(), server_default=sa.text("8"), nullable=False),
    )
    op.add_column(
        "deck_configs",
        sa.Column(
            "leech_action",
            _LEECH_ACTION_ENUM,
            server_default=sa.text("'SUSPEND'::leechaction"),
            nullable=False,
        ),
    )
    op.alter_column("deck_configs", "reviews_dont_bury_new", server_default=None)
    op.alter_column("deck_configs", "leech_threshold", server_default=None)
    op.alter_column("deck_configs", "leech_action", server_default=None)
