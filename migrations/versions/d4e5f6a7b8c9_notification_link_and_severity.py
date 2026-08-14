"""Notification agnosticism: metric_code -> generic link, plus severity field.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notification', sa.Column('link', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('notification', sa.Column('severity', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='info'))
    op.execute("UPDATE notification SET link = '/entries/' || metric_code WHERE metric_code IS NOT NULL")
    op.drop_index(op.f('ix_notification_metric_code'), table_name='notification')
    op.drop_column('notification', 'metric_code')
    op.create_index(op.f('ix_notification_link'), 'notification', ['link'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_notification_link'), table_name='notification')
    op.add_column('notification', sa.Column('metric_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.create_index(op.f('ix_notification_metric_code'), 'notification', ['metric_code'], unique=False)
    op.drop_column('notification', 'severity')
    op.drop_column('notification', 'link')
