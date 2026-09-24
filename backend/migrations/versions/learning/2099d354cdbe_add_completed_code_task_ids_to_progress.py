"""add completed code task ids to progress

Revision ID: 2099d354cdbe
Revises: a9e96d41816e
Create Date: 2026-09-24 10:01:47.008509

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2099d354cdbe"
down_revision: Union[str, Sequence[str], None] = "a9e96d41816e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "progress",
        sa.Column(
            "completed_code_task_ids", sa.JSON(), nullable=False, server_default="[]"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("progress", "completed_code_task_ids")
