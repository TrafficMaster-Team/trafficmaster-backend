"""Add identity and timestamps to answer options."""

from collections.abc import Sequence

from alembic import op

revision: str = "f5a6b7c8d9e0"
down_revision: str | Sequence[str] | None = "e4f5a6b7c8d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE cards
        SET answer_options = (
            SELECT jsonb_agg(
                option || jsonb_build_object(
                    'id', gen_random_uuid()::text,
                    'created_at', CURRENT_TIMESTAMP,
                    'updated_at', CURRENT_TIMESTAMP
                )
                ORDER BY position
            )
            FROM jsonb_array_elements(answer_options) WITH ORDINALITY AS elements(option, position)
        )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE cards
        SET answer_options = (
            SELECT jsonb_agg(
                option - 'id' - 'created_at' - 'updated_at'
                ORDER BY position
            )
            FROM jsonb_array_elements(answer_options) WITH ORDINALITY AS elements(option, position)
        )
        """
    )
