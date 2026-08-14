"""Data-quality follow-ups: notification metric_code, user toggles, flag resolution.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notification', sa.Column('metric_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.create_index(op.f('ix_notification_metric_code'), 'notification', ['metric_code'], unique=False)
    op.add_column('user', sa.Column('dq_notify_hard_bound', sa.Boolean(), nullable=False, server_default=sa.text('1')))
    op.add_column('user', sa.Column('dq_notify_cross_source', sa.Boolean(), nullable=False, server_default=sa.text('1')))
    op.add_column('user', sa.Column('dq_notify_anomaly', sa.Boolean(), nullable=False, server_default=sa.text('1')))
    op.add_column('data_quality_flag', sa.Column('resolved_at', sa.DateTime(), nullable=True))
    op.add_column('data_quality_flag', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('data_quality_flag', 'updated_at')
    op.drop_column('data_quality_flag', 'resolved_at')
    op.drop_column('user', 'dq_notify_anomaly')
    op.drop_column('user', 'dq_notify_cross_source')
    op.drop_column('user', 'dq_notify_hard_bound')
    op.drop_index(op.f('ix_notification_metric_code'), table_name='notification')
    op.drop_column('notification', 'metric_code')
