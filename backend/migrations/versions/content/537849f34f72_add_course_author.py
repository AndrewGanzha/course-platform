'''Add course ownership in the content context.

Revision ID: 537849f34f72
Revises: 18473e67180b
Create Date: 2026-08-27 15:10:36.967742
'''

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '537849f34f72'
down_revision: str | Sequence[str] | None = '18473e67180b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_PARTIAL_TABLES = (
    'question_attempts',
    'answer_options',
    'questions',
    'progress',
)


def _remove_empty_partial_tables() -> None:
    '''Clean up DDL left by the former combined SQLite migration.'''
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = [
        table_name
        for table_name in _PARTIAL_TABLES
        if inspector.has_table(table_name)
    ]

    for table_name in existing_tables:
        table = sa.table(table_name)
        row_count = connection.scalar(
            sa.select(sa.func.count()).select_from(table)
        )
        if row_count:
            raise RuntimeError(
                f'Cannot resume migration: partial table {table_name!r} '
                f'contains {row_count} rows.'
            )

    for table_name in existing_tables:
        op.drop_table(table_name)


def _add_course_author() -> None:
    connection = op.get_bind()
    course_columns = {
        column['name'] for column in sa.inspect(connection).get_columns('courses')
    }

    if 'author_id' not in course_columns:
        op.add_column(
            'courses',
            sa.Column('author_id', sa.String(length=36), nullable=True),
        )

    courses = sa.table(
        'courses',
        sa.column('author_id', sa.String(length=36)),
    )
    users = sa.table(
        'users',
        sa.column('id', sa.String(length=36)),
        sa.column('role', sa.String(length=50)),
    )

    courses_without_author = connection.scalar(
        sa.select(sa.func.count())
        .select_from(courses)
        .where(courses.c.author_id.is_(None))
    )
    if courses_without_author:
        admin_ids = connection.execute(
            sa.select(users.c.id)
            .where(users.c.role == 'admin')
            .order_by(users.c.id)
        ).scalars().all()
        if len(admin_ids) != 1:
            raise RuntimeError(
                'Cannot assign legacy courses to an owner: expected exactly '
                f'one admin user, found {len(admin_ids)}.'
            )

        connection.execute(
            courses.update()
            .where(courses.c.author_id.is_(None))
            .values(author_id=admin_ids[0])
        )

    course_schema = sa.inspect(connection)
    author_column = next(
        column
        for column in course_schema.get_columns('courses')
        if column['name'] == 'author_id'
    )
    needs_not_null = author_column['nullable']
    needs_index = not any(
        index['name'] == 'ix_courses_author_id'
        for index in course_schema.get_indexes('courses')
    )
    needs_foreign_key = not any(
        foreign_key['constrained_columns'] == ['author_id']
        and foreign_key['referred_table'] == 'users'
        and foreign_key['referred_columns'] == ['id']
        and foreign_key.get('options', {}).get('ondelete') == 'CASCADE'
        for foreign_key in course_schema.get_foreign_keys('courses')
    )

    if needs_not_null or needs_index or needs_foreign_key:
        with op.batch_alter_table('courses') as batch_op:
            if needs_not_null:
                batch_op.alter_column(
                    'author_id',
                    existing_type=sa.String(length=36),
                    nullable=False,
                )
            if needs_index:
                batch_op.create_index(
                    op.f('ix_courses_author_id'),
                    ['author_id'],
                    unique=False,
                )
            if needs_foreign_key:
                batch_op.create_foreign_key(
                    'fk_courses_author_id_users',
                    'users',
                    ['author_id'],
                    ['id'],
                    ondelete='CASCADE',
                )


def upgrade() -> None:
    _remove_empty_partial_tables()
    _add_course_author()


def downgrade() -> None:
    with op.batch_alter_table('courses') as batch_op:
        batch_op.drop_constraint(
            'fk_courses_author_id_users',
            type_='foreignkey',
        )
        batch_op.drop_index(op.f('ix_courses_author_id'))
        batch_op.drop_column('author_id')
