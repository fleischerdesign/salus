"""Add colorblind and accent_hue columns to user.

Revision ID: a7c1d2e3f4a5
Revises: f1a2b3c4d5e6
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a7c1d2e3f4a5'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cross-device theme fields to user."""
    op.add_column(
        'user',
        sa.Column('colorblind', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column('user', sa.Column('accent_hue', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Drop the theme fields."""
    op.drop_column('user', 'accent_hue')
    op.drop_column('user', 'colorblind')
