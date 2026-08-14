"""Add lab results and fasting domains.

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-08-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'a7c1d2e3f4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('lab_marker',
    sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('reference_low', sa.Float(), nullable=True),
    sa.Column('reference_high', sa.Float(), nullable=True),
    sa.Column('optimal_low', sa.Float(), nullable=True),
    sa.Column('optimal_high', sa.Float(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['code'], ['metric_definition.code'], ),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_lab_marker_category'), 'lab_marker', ['category'], unique=False)
    op.create_table('lab_panel',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('collection_date', sa.Date(), nullable=False),
    sa.Column('lab_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('fasting', sa.Boolean(), nullable=False),
    sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('attachment_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lab_panel_user_id'), 'lab_panel', ['user_id'], unique=False)
    op.create_table('lab_result',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('panel_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('metric_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('unit', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_abnormal', sa.Boolean(), nullable=False),
    sa.Column('reference_low', sa.Float(), nullable=True),
    sa.Column('reference_high', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['metric_code'], ['metric_definition.code'], ),
    sa.ForeignKeyConstraint(['panel_id'], ['lab_panel.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lab_result_metric_code'), 'lab_result', ['metric_code'], unique=False)
    op.create_index(op.f('ix_lab_result_panel_id'), 'lab_result', ['panel_id'], unique=False)
    op.create_index(op.f('ix_lab_result_user_id'), 'lab_result', ['user_id'], unique=False)
    op.create_table('fasting_session',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.Column('target_hours', sa.Float(), nullable=False),
    sa.Column('fasting_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('water_only', sa.Boolean(), nullable=False),
    sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('mood_during', sa.Integer(), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fasting_session_user_id'), 'fasting_session', ['user_id'], unique=False)
    op.create_table('fasting_protocol',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('fasting_hours', sa.Float(), nullable=False),
    sa.Column('eating_window_hours', sa.Float(), nullable=False),
    sa.Column('schedule_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('target_days_per_week', sa.Integer(), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fasting_protocol_user_id'), 'fasting_protocol', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_fasting_protocol_user_id'), table_name='fasting_protocol')
    op.drop_table('fasting_protocol')
    op.drop_index(op.f('ix_fasting_session_user_id'), table_name='fasting_session')
    op.drop_table('fasting_session')
    op.drop_index(op.f('ix_lab_result_user_id'), table_name='lab_result')
    op.drop_index(op.f('ix_lab_result_panel_id'), table_name='lab_result')
    op.drop_index(op.f('ix_lab_result_metric_code'), table_name='lab_result')
    op.drop_table('lab_result')
    op.drop_index(op.f('ix_lab_panel_user_id'), table_name='lab_panel')
    op.drop_table('lab_panel')
    op.drop_index(op.f('ix_lab_marker_category'), table_name='lab_marker')
    op.drop_table('lab_marker')
