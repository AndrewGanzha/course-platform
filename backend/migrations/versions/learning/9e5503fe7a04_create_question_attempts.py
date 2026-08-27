'''Create the question attempts table for the learning context.

Revision ID: 9e5503fe7a04
Revises: 88447622b6d8
Create Date: 2026-08-27 15:10:36.967742
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '9e5503fe7a04'
down_revision: str | Sequence[str] | None = '88447622b6d8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'question_attempts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=36), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('selected_option_ids', sa.JSON(), nullable=False),
        sa.Column('result_status', sa.String(length=50), nullable=True),
        sa.Column('awarded_points', sa.Integer(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['question_id'],
            ['questions.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('question_attempts')
