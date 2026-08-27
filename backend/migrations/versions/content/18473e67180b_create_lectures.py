'''Create the lectures table for the content context.

Revision ID: 18473e67180b
Revises: 3f2bd01b9a41
Create Date: 2026-07-26 13:41:08.987019
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '18473e67180b'
down_revision: str | Sequence[str] | None = '3f2bd01b9a41'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'lectures',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('section_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['section_id'],
            ['sections.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('lectures')
