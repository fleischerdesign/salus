"""Add Goal.nutrition_field for nutrition sub-field targets.

Revision ID: f2a3b4c5d6e7
Revises: e5f6a7b8c9d0
Create Date: 2026-08-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'goal',
        sa.Column('nutrition_field', sa.Enum('calories', 'protein', 'carbs', 'fat', name='nutritionfield'), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('goal', 'nutrition_field')
