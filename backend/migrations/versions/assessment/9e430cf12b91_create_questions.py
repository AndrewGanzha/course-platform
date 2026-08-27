'''Create the questions table for the assessment context.

Revision ID: 9e430cf12b91
Revises: cadce6ff2e20
Create Date: 2026-08-27 15:10:36.967742
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '9e430cf12b91'
down_revision: str | Sequence[str] | None = 'cadce6ff2e20'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('section_id', sa.String(length=36), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('reward_points', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['section_id'],
            ['sections.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('questions')
