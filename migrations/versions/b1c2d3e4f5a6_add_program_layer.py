"""Add Program/ProgramWorkout and move progression scheme to Program.

Revision ID: b1c2d3e4f5a6
Revises: a8b9c0d1e2f3
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a8b9c0d1e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the Program layer; move the progression scheme onto it (ADR-014)."""
    op.create_table(
        'program',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('progression_scheme', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'program_workout',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('program_id', sa.String(), nullable=False),
        sa.Column('workout_id', sa.String(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['program.id']),
        sa.ForeignKeyConstraint(['workout_id'], ['workout.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.drop_column('workout', 'autoreg_mode')
    with op.batch_alter_table('workout_session') as batch_op:
        batch_op.alter_column('autoreg_mode', new_column_name='progression_scheme')
        batch_op.add_column(sa.Column('program_id', sa.String(), nullable=True))
        batch_op.create_foreign_key(
            'fk_workout_session_program_id', 'program', ['program_id'], ['id'],
        )


def downgrade() -> None:
    """Revert the Program layer and restore the scheme on Workout."""
    with op.batch_alter_table('workout_session') as batch_op:
        batch_op.drop_constraint('fk_workout_session_program_id', type_='foreignkey')
        batch_op.drop_column('program_id')
        batch_op.alter_column('progression_scheme', new_column_name='autoreg_mode')
    op.add_column(
        'workout', sa.Column('autoreg_mode', sa.String(), nullable=False, server_default='advisory')
    )
    op.drop_table('program_workout')
    op.drop_table('program')
