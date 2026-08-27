'''Create the progress table for the learning context.

Revision ID: cadce6ff2e20
Revises: 537849f34f72
Create Date: 2026-08-27 15:10:36.967742
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'cadce6ff2e20'
down_revision: str | Sequence[str] | None = '537849f34f72'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'progress',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=36), nullable=False),
        sa.Column('course_id', sa.String(length=36), nullable=False),
        sa.Column('completed_question_ids', sa.JSON(), nullable=False),
        sa.Column('completed_section_ids', sa.JSON(), nullable=False),
        sa.Column('completed_module_ids', sa.JSON(), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['courses.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'student_id',
            'course_id',
            name='uq_progress_student_course',
        ),
    )


def downgrade() -> None:
    op.drop_table('progress')
