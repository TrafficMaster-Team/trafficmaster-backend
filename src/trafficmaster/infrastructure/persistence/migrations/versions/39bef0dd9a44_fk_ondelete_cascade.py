"""fk ondelete cascade

Revision ID: 39bef0dd9a44
Revises: 426eaf5821c5
Create Date: 2026-06-02 00:16:57.161458

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "39bef0dd9a44"
down_revision: str | Sequence[str] | None = "426eaf5821c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# (constraint name, table, referred table, local col, referred col)
_CASCADE_FKS = [
    ("pg_card_progress_user_id_users", "card_progress", "users", "user_id", "id"),
    ("pg_card_progress_card_id_cards", "card_progress", "cards", "card_id", "id"),
    ("pg_review_logs_user_id_users", "review_logs", "users", "user_id", "id"),
    ("pg_review_logs_card_id_cards", "review_logs", "cards", "card_id", "id"),
    ("pg_deck_configs_owner_id_users", "deck_configs", "users", "owner_id", "id"),
    ("pg_cards_deck_id_decks", "cards", "decks", "deck_id", "id"),
    ("pg_decks_owner_id_users", "decks", "users", "owner_id", "id"),
]


def upgrade() -> None:
    """Recreate foreign keys with ON DELETE CASCADE."""
    for name, table, ref, col, ref_col in _CASCADE_FKS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, ref, [col], [ref_col], ondelete="CASCADE")


def downgrade() -> None:
    """Restore foreign keys without ON DELETE CASCADE."""
    for name, table, ref, col, ref_col in _CASCADE_FKS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, ref, [col], [ref_col])
