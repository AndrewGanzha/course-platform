'''Create the modules table for the content context.

Revision ID: 80e91ae7f46d
Revises: 0f26d8e489cb
Create Date: 2026-07-26 13:41:08.987019
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '80e91ae7f46d'
down_revision: str | Sequence[str] | None = '0f26d8e489cb'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'modules',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['courses.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('modules')
