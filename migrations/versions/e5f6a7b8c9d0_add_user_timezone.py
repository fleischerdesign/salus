"""Add user.timezone (IANA) for consistent local day boundaries.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('timezone', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='UTC'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'timezone')
