'''Create the answer options table for the assessment context.

Revision ID: 88447622b6d8
Revises: 9e430cf12b91
Create Date: 2026-08-27 15:10:36.967742
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '88447622b6d8'
down_revision: str | Sequence[str] | None = '9e430cf12b91'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'answer_options',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ['question_id'],
            ['questions.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('answer_options')
