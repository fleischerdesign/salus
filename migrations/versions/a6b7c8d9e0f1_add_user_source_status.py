"""Add UserSourceStatus for account-level source connection state.

Revision ID: a6b7c8d9e0f1
Revises: f2a3b4c5d6e7
Create Date: 2026-08-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a6b7c8d9e0f1'
down_revision: Union[str, Sequence[str], None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_source_status',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('connected', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_source_status_user_id', 'user_source_status', ['user_id'])
    op.create_index('ix_user_source_status_source', 'user_source_status', ['source'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_user_source_status_source', table_name='user_source_status')
    op.drop_index('ix_user_source_status_user_id', table_name='user_source_status')
    op.drop_table('user_source_status')
