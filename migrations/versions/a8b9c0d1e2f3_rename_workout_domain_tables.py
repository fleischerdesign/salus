"""Rename workout domain tables: plan -> workout terminology.

Revision ID: a8b9c0d1e2f3
Revises: a6b7c8d9e0f1
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, Sequence[str], None] = 'a6b7c8d9e0f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename plan terminology to workout (ADR-014)."""
    op.rename_table('workout_plan', 'workout')
    op.rename_table('workout_plan_exercise', 'workout_exercise')
    op.rename_table('workout_log_entry', 'workout_set')
    op.alter_column('workout_exercise', 'plan_id', new_column_name='workout_id')
    op.alter_column('workout_session', 'plan_id', new_column_name='workout_id')


def downgrade() -> None:
    """Revert workout terminology back to plan."""
    op.alter_column('workout_session', 'workout_id', new_column_name='plan_id')
    op.alter_column('workout_exercise', 'workout_id', new_column_name='plan_id')
    op.rename_table('workout_set', 'workout_log_entry')
    op.rename_table('workout_exercise', 'workout_plan_exercise')
    op.rename_table('workout', 'workout_plan')
