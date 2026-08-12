"""Rename metric terminology: data_type / metric_type_code -> source_data_type.

Revision ID: f1a2b3c4d5e6
Revises: 8884149c454a
Create Date: 2026-08-13

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '8884149c454a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename source-channel columns to source_data_type."""
    op.alter_column('measurement', 'data_type', new_column_name='source_data_type')
    op.alter_column(
        'leaderboard_group', 'metric_type_code', new_column_name='source_data_type'
    )
    op.alter_column(
        'federated_measurement_cache', 'data_type', new_column_name='source_data_type'
    )
    op.alter_column(
        'federated_access_log', 'data_type', new_column_name='source_data_type'
    )


def downgrade() -> None:
    """Revert source_data_type columns to their previous names."""
    op.alter_column('measurement', 'source_data_type', new_column_name='data_type')
    op.alter_column(
        'leaderboard_group', 'source_data_type', new_column_name='metric_type_code'
    )
    op.alter_column(
        'federated_measurement_cache', 'source_data_type', new_column_name='data_type'
    )
    op.alter_column(
        'federated_access_log', 'source_data_type', new_column_name='data_type'
    )
