"""Replace a single card answer with quiz answer options and a hint."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e4f5a6b7c8d9"
down_revision: str | Sequence[str] | None = "d1e2f3a4b5c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("cards", sa.Column("answer_options", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("cards", sa.Column("hint", sa.String(length=5000), nullable=True))
    op.execute(
        """
        UPDATE cards
        SET answer_options = jsonb_build_array(
            jsonb_build_object(
                'text', answer,
                'is_correct', true,
                'rationale', 'Correct answer migrated from the previous card format.'
            )
        ),
        hint = 'No hint was provided for this migrated card.'
        """
    )
    op.alter_column("cards", "answer_options", nullable=False)
    op.alter_column("cards", "hint", nullable=False)
    op.drop_column("cards", "answer")


def downgrade() -> None:
    op.add_column("cards", sa.Column("answer", sa.String(length=5000), nullable=True))
    op.execute(
        """
        UPDATE cards
        SET answer = COALESCE(
            (SELECT option->>'text' FROM jsonb_array_elements(answer_options) AS option
             WHERE (option->>'is_correct')::boolean IS TRUE LIMIT 1),
            answer_options->0->>'text'
        )
        """
    )
    op.alter_column("cards", "answer", nullable=False)
    op.drop_column("cards", "hint")
    op.drop_column("cards", "answer_options")
