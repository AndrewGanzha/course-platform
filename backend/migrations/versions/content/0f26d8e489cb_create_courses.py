'''Create the courses table for the content context.

Revision ID: 0f26d8e489cb
Revises: 1df01776e261
Create Date: 2026-07-26 13:41:08.987019
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '0f26d8e489cb'
down_revision: str | Sequence[str] | None = '1df01776e261'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'courses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('courses')
