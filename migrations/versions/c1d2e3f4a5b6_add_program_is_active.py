"""Add Program.is_active for program activation.

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-08-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Program.is_active."""
    op.add_column(
        'program',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Drop Program.is_active."""
    op.drop_column('program', 'is_active')
