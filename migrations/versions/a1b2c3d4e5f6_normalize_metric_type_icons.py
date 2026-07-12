"""normalize_metric_type_icons_underscores_to_hyphens

Revision ID: a1b2c3d4e5f6
Revises: 87d69535bc18
Create Date: 2026-07-10 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "87d69535bc18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace underscores with hyphens in metric_type.icon for known icon names."""
    icons_to_migrate = [
        ("directions_walk", "directions-walk"),
        ("monitor_heart", "monitor-heart"),
        ("monitor_weight", "monitor-weight"),
        ("vital_signs", "vital-signs"),
        ("body_fat", "body-fat"),
        ("water_drop", "water-drop"),
    ]
    for old, new in icons_to_migrate:
        op.execute(
            sa.text(
                "UPDATE metric_type SET icon = :new WHERE icon = :old"
            ).bindparams(old=old, new=new)
        )


def downgrade() -> None:
    """Revert hyphens back to underscores for known icon names."""
    icons_to_migrate = [
        ("directions-walk", "directions_walk"),
        ("monitor-heart", "monitor_heart"),
        ("monitor-weight", "monitor_weight"),
        ("vital-signs", "vital_signs"),
        ("body-fat", "body_fat"),
        ("water-drop", "water_drop"),
    ]
    for old, new in icons_to_migrate:
        op.execute(
            sa.text(
                "UPDATE metric_type SET icon = :new WHERE icon = :old"
            ).bindparams(old=old, new=new)
        )
