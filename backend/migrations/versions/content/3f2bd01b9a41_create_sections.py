'''Create the sections table for the content context.

Revision ID: 3f2bd01b9a41
Revises: 80e91ae7f46d
Create Date: 2026-07-26 13:41:08.987019
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '3f2bd01b9a41'
down_revision: str | Sequence[str] | None = '80e91ae7f46d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'sections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('module_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['module_id'],
            ['modules.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('sections')
