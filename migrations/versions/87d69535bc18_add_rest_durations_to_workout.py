"""add_rest_durations_to_workout

Revision ID: 87d69535bc18
Revises: 5c4525ac71bb
Create Date: 2026-07-09 01:26:41.147890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87d69535bc18'
down_revision: Union[str, Sequence[str], None] = '5c4525ac71bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('workout_plan_exercise', sa.Column('rest_seconds', sa.Integer(), nullable=True))
    op.add_column('exercise', sa.Column('suggested_rest_seconds', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('workout_plan_exercise', 'rest_seconds')
    op.drop_column('exercise', 'suggested_rest_seconds')
