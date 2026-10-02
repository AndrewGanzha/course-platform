import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.presentation.api.dependencies as api_dependencies
from app.infrastructure.config import get_settings
from app.infrastructure.database.models import (
    AnswerOptionModel,
    Base,
    CodeSubmissionModel,
    CodeTaskModel,
    CourseModel,
    CourseReviewModel,
    LectureCommentModel,
    LectureModel,
    ModuleModel,
    ProgressModel,
    QuestionAttemptModel,
    QuestionModel,
    SectionModel,
    TaskAttemptModel,
    TaskModel,
    TestCaseModel,
    UserModel,
)
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.main import create_app


@pytest.fixture(scope="session", autouse=True)
def media_root(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("media")
    os.environ["MEDIA_ROOT"] = str(root)
    os.environ["MAX_COVER_IMAGE_BYTES"] = str(1024 * 1024)
    get_settings.cache_clear()
    return root


@pytest_asyncio.fixture(scope="session")
async def test_engine(tmp_path_factory) -> AsyncIterator:
    database_dir = tmp_path_factory.mktemp("test_db")
    database_path = Path(database_dir) / "test_fastapi_education.db"
    database_url = f"sqlite+aiosqlite:///{database_path}"

    engine = create_async_engine(database_url, future=True, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if database_path.exists():
        os.remove(database_path)


@pytest.fixture
def session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture(autouse=True)
async def clear_database(session_factory) -> None:
    async with session_factory() as session:
        for model in [
            CourseReviewModel,
            LectureCommentModel,
            AnswerOptionModel,
            QuestionAttemptModel,
            ProgressModel,
            QuestionModel,
            TaskAttemptModel,
            TestCaseModel,
            CodeSubmissionModel,
            TaskModel,
            CodeTaskModel,
            LectureModel,
            SectionModel,
            ModuleModel,
            CourseModel,
            UserModel,
        ]:
            await session.execute(delete(model))
        await session.commit()


@pytest_asyncio.fixture
async def app(session_factory):
    app = create_app()
    original_session_factory = api_dependencies.SessionFactory
    api_dependencies.SessionFactory = session_factory
    try:
        yield app
    finally:
        api_dependencies.SessionFactory = original_session_factory


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def seeded_course_tree(session_factory, seeded_admin_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    lecture_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_admin_user.id,
            title="FastAPI course",
            description="Clean architecture in practice.",
            short_description="Build a production-ready learning backend.",
            cover_image_url="https://example.com/fastapi-course-cover.png",
            difficulty="intermediate",
            tag_names=["fastapi", "backend", "architecture"],
            status="published",
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title="MVP stage",
            description="Content, users and access.",
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title="Auth section",
            description="JWT and route protection.",
            position=1,
        )
        lecture = LectureModel(
            id=lecture_id,
            section_id=section_id,
            title="Bearer token in practice",
            content="Lecture content",
            position=1,
        )
        session.add_all([course, module, section, lecture])
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        author_id=seeded_admin_user.id,
        module_id=module_id,
        section_id=section_id,
        lecture_id=lecture_id,
        course_title="FastAPI course",
        course_short_description="Build a production-ready learning backend.",
        course_cover_image_url="https://example.com/fastapi-course-cover.png",
        course_difficulty="intermediate",
        course_tag_names=["fastapi", "backend", "architecture"],
        course_average_rating=0.0,
        course_reviews_count=0,
        lecture_content="Lecture content",
    )


@pytest_asyncio.fixture
async def seeded_student_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email="student@example.com",
            hashed_password=hasher.hash("strongpassword123"),
            role="student",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def seeded_admin_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email="admin@example.com",
            hashed_password=hasher.hash("strongpassword123"),
            role="admin",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def seeded_author_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email="author@example.com",
            hashed_password=hasher.hash("strongpassword123"),
            role="author",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def seeded_other_author_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email="other-author@example.com",
            hashed_password=hasher.hash("strongpassword123"),
            role="author",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def seeded_interactive_tree(session_factory, seeded_author_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    lecture_id = str(uuid4())
    question_id = str(uuid4())
    wrong_option_id = str(uuid4())
    correct_option_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_author_user.id,
            title="Interactive FastAPI",
            description="Course with questions inside sections.",
            status="published",
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title="HTTP",
            description="Methods",
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title="Basics",
            description="Intro section",
            position=1,
        )
        lecture = LectureModel(
            id=lecture_id,
            section_id=section_id,
            title="GET and POST",
            content="Lecture content",
            position=1,
        )
        question = QuestionModel(
            id=question_id,
            section_id=section_id,
            text="Which method reads a resource?",
            position=1,
            question_type="single_choice",
            max_attempts=2,
            reward_points=5,
        )
        wrong_option = AnswerOptionModel(
            id=wrong_option_id,
            question_id=question_id,
            text="POST",
            position=1,
            is_correct=False,
        )
        correct_option = AnswerOptionModel(
            id=correct_option_id,
            question_id=question_id,
            text="GET",
            position=2,
            is_correct=True,
        )

        session.add_all(
            [
                course,
                module,
                section,
                lecture,
                question,
                wrong_option,
                correct_option,
            ]
        )
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        module_id=module_id,
        section_id=section_id,
        lecture_id=lecture_id,
        question_id=question_id,
        wrong_option_id=wrong_option_id,
        correct_option_id=correct_option_id,
    )


@pytest_asyncio.fixture
async def seeded_draft_lecture_tree(session_factory, seeded_author_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    lecture_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_author_user.id,
            title="Draft discussion course",
            description="Draft course hidden from students.",
            status="draft",
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title="Draft module",
            description="Draft module",
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title="Draft section",
            description="Draft section",
            position=1,
        )
        lecture = LectureModel(
            id=lecture_id,
            section_id=section_id,
            title="Draft lecture",
            content="Draft content",
            position=1,
        )
        session.add_all([course, module, section, lecture])
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        module_id=module_id,
        section_id=section_id,
        lecture_id=lecture_id,
    )


@pytest_asyncio.fixture
async def seeded_code_task_tree(session_factory, seeded_author_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    lecture_id = str(uuid4())
    code_task_id = str(uuid4())
    test_case_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_author_user.id,
            title="Code task course",
            description="Course with a code task inside.",
            status="published",
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title="Practice",
            description="Coding practice",
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title="Basics",
            description="Intro section",
            position=1,
        )
        lecture = LectureModel(
            id=lecture_id,
            section_id=section_id,
            title="Warm up",
            content="Lecture content",
            position=1,
        )
        code_task = CodeTaskModel(
            id=code_task_id,
            section_id=section_id,
            title="Sum numbers",
            statement="Read two integers and print their sum.",
            position=1,
            language="python",
            starter_code="a, b = map(int, input().split())",
            max_attempts=3,
            reward_points=5,
            time_limit_seconds=20,
            memory_limit_mb=128,
        )
        test_case = TestCaseModel(
            id=test_case_id,
            code_task_id=code_task_id,
            position=1,
            input_data="2 3",
            expected_output="5",
            is_hidden=False,
            explanation="basic case",
        )

        session.add_all([course, module, section, lecture, code_task, test_case])
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        module_id=module_id,
        section_id=section_id,
        lecture_id=lecture_id,
        code_task_id=code_task_id,
        test_case_id=test_case_id,
    )


@pytest_asyncio.fixture
async def student_auth_headers(client, seeded_student_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "student@example.com",
            "password": "strongpassword123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(client, seeded_admin_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "admin@example.com",
            "password": "strongpassword123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def author_auth_headers(client, seeded_author_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "author@example.com",
            "password": "strongpassword123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def other_author_auth_headers(client, seeded_other_author_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "other-author@example.com",
            "password": "strongpassword123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def seeded_author_analytics_tree(
    session_factory,
    seeded_author_user,
    seeded_student_user,
):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    question_id = str(uuid4())
    wrong_option_id = str(uuid4())
    correct_option_id = str(uuid4())
    task_id = str(uuid4())
    code_task_id = str(uuid4())
    second_student_id = str(uuid4())
    now = datetime.now(UTC)

    hasher = PwdlibPasswordHasher()
    second_student = UserModel(
        id=second_student_id,
        email="analytics-student@example.com",
        hashed_password=hasher.hash("strongpassword123"),
        role="student",
    )

    course = CourseModel(
        id=course_id,
        author_id=seeded_author_user.id,
        title="Author analytics course",
        description="Course prepared for author analytics tests.",
        status="published",
    )
    module = ModuleModel(
        id=module_id,
        course_id=course_id,
        title="Analytics module",
        description="Module with all learning activity types.",
        position=1,
    )
    section = SectionModel(
        id=section_id,
        module_id=module_id,
        title="Analytics section",
        description="Section for aggregated analytics.",
        position=1,
    )
    question = QuestionModel(
        id=question_id,
        section_id=section_id,
        text="Which HTTP method reads a resource?",
        position=1,
        question_type="single_choice",
        max_attempts=3,
        reward_points=5,
    )
    wrong_option = AnswerOptionModel(
        id=wrong_option_id,
        question_id=question_id,
        text="POST",
        position=1,
        is_correct=False,
    )
    correct_option = AnswerOptionModel(
        id=correct_option_id,
        question_id=question_id,
        text="GET",
        position=2,
        is_correct=True,
    )
    task = TaskModel(
        id=task_id,
        section_id=section_id,
        title="HTTP method",
        statement="Enter GET.",
        position=1,
        check_type="exact_match",
        expected_answer="GET",
        accepted_answers=[],
        answer_pattern="",
        max_attempts=3,
        reward_points=3,
    )
    code_task = CodeTaskModel(
        id=code_task_id,
        section_id=section_id,
        title="Sum numbers",
        statement="Read two integers and print their sum.",
        position=2,
        language="python",
        starter_code="a, b = map(int, input().split())",
        max_attempts=3,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )

    first_student_question_attempts = [
        QuestionAttemptModel(
            id=str(uuid4()),
            question_id=question_id,
            student_id=seeded_student_user.id,
            attempt_number=1,
            selected_option_ids=[wrong_option_id],
            result_status="incorrect",
            awarded_points=0,
            checked_at=now,
            created_at=now,
        ),
        QuestionAttemptModel(
            id=str(uuid4()),
            question_id=question_id,
            student_id=seeded_student_user.id,
            attempt_number=2,
            selected_option_ids=[correct_option_id],
            result_status="correct",
            awarded_points=5,
            checked_at=now,
            created_at=now,
        ),
    ]
    second_student_question_attempt = QuestionAttemptModel(
        id=str(uuid4()),
        question_id=question_id,
        student_id=second_student_id,
        attempt_number=1,
        selected_option_ids=[correct_option_id],
        result_status="correct",
        awarded_points=5,
        checked_at=now,
        created_at=now,
    )

    first_student_task_attempts = [
        TaskAttemptModel(
            id=str(uuid4()),
            task_id=task_id,
            student_id=seeded_student_user.id,
            submitted_answer="POST",
            attempt_number=1,
            status="incorrect",
            awarded_points=0,
            checked_at=now,
            created_at=now,
        ),
        TaskAttemptModel(
            id=str(uuid4()),
            task_id=task_id,
            student_id=seeded_student_user.id,
            submitted_answer="GET",
            attempt_number=2,
            status="correct",
            awarded_points=3,
            checked_at=now,
            created_at=now,
        ),
    ]
    second_student_task_attempt = TaskAttemptModel(
        id=str(uuid4()),
        task_id=task_id,
        student_id=second_student_id,
        submitted_answer="GET",
        attempt_number=1,
        status="correct",
        awarded_points=3,
        checked_at=now,
        created_at=now,
    )

    first_student_submissions = [
        CodeSubmissionModel(
            id=str(uuid4()),
            code_task_id=code_task_id,
            student_id=seeded_student_user.id,
            source_code="print(0)",
            attempt_number=1,
            status="failed",
            created_at=now,
            started_at=now,
            finished_at=now,
        ),
        CodeSubmissionModel(
            id=str(uuid4()),
            code_task_id=code_task_id,
            student_id=seeded_student_user.id,
            source_code="a, b = map(int, input().split()); print(a + b)",
            attempt_number=2,
            status="passed",
            created_at=now,
            started_at=now,
            finished_at=now,
        ),
    ]
    second_student_submission = CodeSubmissionModel(
        id=str(uuid4()),
        code_task_id=code_task_id,
        student_id=second_student_id,
        source_code="print(0)",
        attempt_number=1,
        status="failed",
        created_at=now,
        started_at=now,
        finished_at=now,
    )

    completed_progress = ProgressModel(
        id=str(uuid4()),
        student_id=seeded_student_user.id,
        course_id=course_id,
        completed_question_ids=[question_id],
        completed_task_ids=[task_id],
        completed_code_task_ids=[code_task_id],
        completed_section_ids=[section_id],
        completed_module_ids=[module_id],
        total_points=13,
    )
    partial_progress = ProgressModel(
        id=str(uuid4()),
        student_id=second_student_id,
        course_id=course_id,
        completed_question_ids=[question_id],
        completed_task_ids=[task_id],
        completed_code_task_ids=[],
        completed_section_ids=[],
        completed_module_ids=[],
        total_points=8,
    )

    async with session_factory() as session:
        session.add_all(
            [
                second_student,
                course,
                module,
                section,
                question,
                wrong_option,
                correct_option,
                task,
                code_task,
                *first_student_question_attempts,
                second_student_question_attempt,
                *first_student_task_attempts,
                second_student_task_attempt,
                *first_student_submissions,
                second_student_submission,
                completed_progress,
                partial_progress,
            ]
        )
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        course_title="Author analytics course",
        module_id=module_id,
        section_id=section_id,
        question_id=question_id,
        task_id=task_id,
        code_task_id=code_task_id,
    )


@pytest_asyncio.fixture
async def seeded_review_eligibility(
    session_factory,
    seeded_author_user,
    seeded_student_user,
):
    eligible_course_id = str(uuid4())
    eligible_module_id = str(uuid4())
    eligible_section_ids = [str(uuid4()) for _ in range(5)]

    ineligible_course_id = str(uuid4())
    ineligible_module_id = str(uuid4())
    ineligible_section_ids = [str(uuid4()) for _ in range(5)]

    eligible_course = CourseModel(
        id=eligible_course_id,
        author_id=seeded_author_user.id,
        title="Review eligible course",
        description="Course completed by exactly eighty percent.",
        status="published",
    )
    eligible_module = ModuleModel(
        id=eligible_module_id,
        course_id=eligible_course_id,
        title="Eligible module",
        description="Five sections for the boundary test.",
        position=1,
    )
    eligible_sections = [
        SectionModel(
            id=section_id,
            module_id=eligible_module_id,
            title=f"Eligible section {position}",
            description="Review eligibility section.",
            position=position,
        )
        for position, section_id in enumerate(eligible_section_ids, start=1)
    ]
    eligible_progress = ProgressModel(
        id=str(uuid4()),
        student_id=seeded_student_user.id,
        course_id=eligible_course_id,
        completed_question_ids=[],
        completed_task_ids=[],
        completed_code_task_ids=[],
        completed_section_ids=eligible_section_ids[:4],
        completed_module_ids=[],
        total_points=0,
    )

    ineligible_course = CourseModel(
        id=ineligible_course_id,
        author_id=seeded_author_user.id,
        title="Review ineligible course",
        description="Course completed by only sixty percent.",
        status="published",
    )
    ineligible_module = ModuleModel(
        id=ineligible_module_id,
        course_id=ineligible_course_id,
        title="Ineligible module",
        description="Five sections below the boundary.",
        position=1,
    )
    ineligible_sections = [
        SectionModel(
            id=section_id,
            module_id=ineligible_module_id,
            title=f"Ineligible section {position}",
            description="Review eligibility section.",
            position=position,
        )
        for position, section_id in enumerate(ineligible_section_ids, start=1)
    ]
    ineligible_progress = ProgressModel(
        id=str(uuid4()),
        student_id=seeded_student_user.id,
        course_id=ineligible_course_id,
        completed_question_ids=[],
        completed_task_ids=[],
        completed_code_task_ids=[],
        completed_section_ids=ineligible_section_ids[:3],
        completed_module_ids=[],
        total_points=0,
    )

    async with session_factory() as session:
        session.add_all(
            [
                eligible_course,
                eligible_module,
                *eligible_sections,
                eligible_progress,
                ineligible_course,
                ineligible_module,
                *ineligible_sections,
                ineligible_progress,
            ]
        )
        await session.commit()

    return SimpleNamespace(
        eligible_course_id=eligible_course_id,
        ineligible_course_id=ineligible_course_id,
    )
