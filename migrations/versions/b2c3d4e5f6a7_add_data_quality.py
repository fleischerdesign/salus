"""Add data quality: metric_definition bounds and data_quality_flag table.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('metric_definition', sa.Column('min_value', sa.Float(), nullable=True))
    op.add_column('metric_definition', sa.Column('max_value', sa.Float(), nullable=True))
    op.create_table('data_quality_flag',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('metric_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('measurement_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('severity', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('context_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['metric_code'], ['metric_definition.code'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_quality_flag_user_id'), 'data_quality_flag', ['user_id'], unique=False)
    op.create_index(op.f('ix_data_quality_flag_kind'), 'data_quality_flag', ['kind'], unique=False)
    op.create_index(op.f('ix_data_quality_flag_measurement_id'), 'data_quality_flag', ['measurement_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_data_quality_flag_measurement_id'), table_name='data_quality_flag')
    op.drop_index(op.f('ix_data_quality_flag_kind'), table_name='data_quality_flag')
    op.drop_index(op.f('ix_data_quality_flag_user_id'), table_name='data_quality_flag')
    op.drop_table('data_quality_flag')
    op.drop_column('metric_definition', 'max_value')
    op.drop_column('metric_definition', 'min_value')
