"""Add status column to sharing_relationship

Revision ID: 4b8c3f2d1a9e
Revises: ffa8baefa444
Create Date: 2026-07-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4b8c3f2d1a9e'
down_revision: Union[str, Sequence[str], None] = 'ffa8baefa444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'sharing_relationship',
        sa.Column('status', sa.String(), nullable=False, server_default='active')
    )
    with op.batch_alter_table('sharing_relationship') as batch_op:
        batch_op.drop_column('is_active')


def downgrade() -> None:
    op.add_column(
        'sharing_relationship',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.true())
    )
    with op.batch_alter_table('sharing_relationship') as batch_op:
        batch_op.drop_column('status')
