import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


BACKEND_ROOT = Path(__file__).resolve().parents[3]
ALEMBIC_CONFIG = BACKEND_ROOT / 'alembic.ini'

REVISION_CHAIN = [
    '1df01776e261',
    '0f26d8e489cb',
    '80e91ae7f46d',
    '3f2bd01b9a41',
    '18473e67180b',
    '537849f34f72',
    'cadce6ff2e20',
    '9e430cf12b91',
    '88447622b6d8',
    '9e5503fe7a04',
]
INITIAL_REVISION = '18473e67180b'
HEAD_REVISION = '9e5503fe7a04'

INITIAL_TABLES = {
    'courses',
    'lectures',
    'modules',
    'sections',
    'users',
}
HEAD_TABLES = INITIAL_TABLES | {
    'answer_options',
    'progress',
    'question_attempts',
    'questions',
}


def _run_alembic(
    database_path: Path,
    *arguments: str,
    succeeds: bool = True,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment['DATABASE_URL'] = (
        f'sqlite+aiosqlite:///{database_path.as_posix()}'
    )
    result = subprocess.run(
        [sys.executable, '-m', 'alembic', *arguments],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    if succeeds:
        assert result.returncode == 0, output
    else:
        assert result.returncode != 0, output
    return result


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        '''
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        '''
    )
    return {row[0] for row in rows}


def _current_revision(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        'SELECT version_num FROM alembic_version'
    ).fetchone()
    assert row is not None
    return row[0]


def _seed_initial_course_tree(connection: sqlite3.Connection) -> None:
    connection.execute(
        'INSERT INTO users (id, email, hashed_password, role) VALUES (?, ?, ?, ?)',
        ('admin-id', 'admin@example.com', 'hash', 'admin'),
    )
    connection.execute(
        'INSERT INTO courses (id, title, description) VALUES (?, ?, ?)',
        ('course-id', 'Course', 'Description'),
    )
    connection.execute(
        '''
        INSERT INTO modules (id, course_id, title, description, position)
        VALUES (?, ?, ?, ?, ?)
        ''',
        ('module-id', 'course-id', 'Module', 'Description', 1),
    )
    connection.execute(
        '''
        INSERT INTO sections (id, module_id, title, description, position)
        VALUES (?, ?, ?, ?, ?)
        ''',
        ('section-id', 'module-id', 'Section', 'Description', 1),
    )
    connection.execute(
        '''
        INSERT INTO lectures (id, section_id, title, content, position)
        VALUES (?, ?, ?, ?, ?)
        ''',
        ('lecture-id', 'section-id', 'Lecture', 'Content', 1),
    )
    connection.commit()


def test_revision_chain_is_linear_and_grouped_by_context() -> None:
    scripts = ScriptDirectory.from_config(Config(ALEMBIC_CONFIG))
    revisions = list(reversed(list(scripts.walk_revisions())))

    assert [revision.revision for revision in revisions] == REVISION_CHAIN
    assert scripts.get_bases() == [REVISION_CHAIN[0]]
    assert scripts.get_heads() == [HEAD_REVISION]
    assert {
        Path(revision.path).parent.name for revision in revisions
    } == {'identity', 'content', 'assessment', 'learning'}


def test_fresh_database_upgrades_and_downgrades_cleanly(tmp_path: Path) -> None:
    database_path = tmp_path / 'fresh.db'

    _run_alembic(database_path, 'upgrade', 'head')
    check_result = _run_alembic(database_path, 'check')

    assert 'No new upgrade operations detected.' in check_result.stdout
    with sqlite3.connect(database_path) as connection:
        assert _current_revision(connection) == HEAD_REVISION
        assert _table_names(connection) == HEAD_TABLES | {'alembic_version'}

        course_columns = {
            row[1]: row for row in connection.execute('PRAGMA table_info(courses)')
        }
        assert course_columns['author_id'][3] == 1

        course_indexes = {
            row[1] for row in connection.execute('PRAGMA index_list(courses)')
        }
        user_indexes = {
            row[1] for row in connection.execute('PRAGMA index_list(users)')
        }
        assert 'ix_courses_author_id' in course_indexes
        assert 'ix_users_email' in user_indexes

        course_foreign_keys = list(
            connection.execute('PRAGMA foreign_key_list(courses)')
        )
        assert any(
            row[2] == 'users'
            and row[3] == 'author_id'
            and row[4] == 'id'
            and row[6] == 'CASCADE'
            for row in course_foreign_keys
        )

        progress_sql = connection.execute(
            'SELECT sql FROM sqlite_master WHERE name = ?',
            ('progress',),
        ).fetchone()[0]
        assert 'uq_progress_student_course' in progress_sql

    _run_alembic(database_path, 'downgrade', 'base')
    with sqlite3.connect(database_path) as connection:
        assert not (_table_names(connection) & HEAD_TABLES)

    _run_alembic(database_path, 'upgrade', 'head')
    with sqlite3.connect(database_path) as connection:
        assert _current_revision(connection) == HEAD_REVISION


def test_initial_milestone_preserves_data_across_upgrade_and_downgrade(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / 'initial-milestone.db'
    _run_alembic(database_path, 'upgrade', INITIAL_REVISION)

    with sqlite3.connect(database_path) as connection:
        assert _current_revision(connection) == INITIAL_REVISION
        assert _table_names(connection) == INITIAL_TABLES | {'alembic_version'}
        course_columns = {
            row[1] for row in connection.execute('PRAGMA table_info(courses)')
        }
        assert 'author_id' not in course_columns
        _seed_initial_course_tree(connection)

    _run_alembic(database_path, 'upgrade', 'head')
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            'SELECT author_id FROM courses WHERE id = ?',
            ('course-id',),
        ).fetchone() == ('admin-id',)
        assert all(
            connection.execute(
                f'SELECT count(*) FROM {table_name}'
            ).fetchone()[0] == 1
            for table_name in INITIAL_TABLES
        )

    _run_alembic(database_path, 'downgrade', INITIAL_REVISION)
    with sqlite3.connect(database_path) as connection:
        assert _current_revision(connection) == INITIAL_REVISION
        assert _table_names(connection) == INITIAL_TABLES | {'alembic_version'}
        course_columns = {
            row[1] for row in connection.execute('PRAGMA table_info(courses)')
        }
        assert 'author_id' not in course_columns
        assert all(
            connection.execute(
                f'SELECT count(*) FROM {table_name}'
            ).fetchone()[0] == 1
            for table_name in INITIAL_TABLES
        )


def test_empty_partial_tables_are_recovered_before_split_migrations(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / 'partial-empty.db'
    _run_alembic(database_path, 'upgrade', INITIAL_REVISION)

    with sqlite3.connect(database_path) as connection:
        _seed_initial_course_tree(connection)
        connection.execute('ALTER TABLE courses ADD COLUMN author_id VARCHAR(36)')
        for table_name in (
            'progress',
            'questions',
            'answer_options',
            'question_attempts',
        ):
            connection.execute(
                f'CREATE TABLE {table_name} (id VARCHAR(36) PRIMARY KEY)'
            )
        connection.commit()

    _run_alembic(database_path, 'upgrade', 'head')
    with sqlite3.connect(database_path) as connection:
        assert _current_revision(connection) == HEAD_REVISION
        assert connection.execute(
            'SELECT author_id FROM courses WHERE id = ?',
            ('course-id',),
        ).fetchone() == ('admin-id',)
        question_columns = {
            row[1] for row in connection.execute('PRAGMA table_info(questions)')
        }
        assert 'section_id' in question_columns


def test_nonempty_partial_table_is_never_dropped(tmp_path: Path) -> None:
    database_path = tmp_path / 'partial-with-data.db'
    _run_alembic(database_path, 'upgrade', INITIAL_REVISION)

    with sqlite3.connect(database_path) as connection:
        connection.execute('CREATE TABLE progress (id VARCHAR(36) PRIMARY KEY)')
        connection.execute('INSERT INTO progress (id) VALUES (?)', ('progress-id',))
        connection.commit()

    result = _run_alembic(
        database_path,
        'upgrade',
        'head',
        succeeds=False,
    )

    assert 'partial table \'progress\' contains 1 rows' in result.stderr
    with sqlite3.connect(database_path) as connection:
        assert connection.execute('SELECT count(*) FROM progress').fetchone() == (1,)
