"""add_locale_to_user

Revision ID: d6cb86c8ccd6
Revises: 42bde208c7ba
Create Date: 2026-07-11 21:08:19.082680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd6cb86c8ccd6'
down_revision: Union[str, Sequence[str], None] = '42bde208c7ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('locale', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='en'))


def downgrade() -> None:
    op.drop_column('user', 'locale')
