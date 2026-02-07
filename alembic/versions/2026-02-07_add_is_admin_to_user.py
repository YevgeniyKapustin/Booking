"""add is_admin to user

Revision ID: 9b5a1e8b0f3c
Revises: 75b364ae0ee4
Create Date: 2026-02-07 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b5a1e8b0f3c"
down_revision: Union[str, Sequence[str], None] = "75b364ae0ee4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "usr",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("usr", "is_admin")
