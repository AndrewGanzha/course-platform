from uuid import uuid4

import pytest

from app.application.exceptions import CoursePublicationNotReadyError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.use_cases.courses.publish_course import (
    PublishCourseCommand,
    PublishCourseUseCase,
)
from app.domain.entities.course import Course
from app.domain.entities.user import User, UserRole


class FakeCourseRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, course_id):
        return self.items.get(course_id)

    async def update(self, course):
        self.items[course.id] = course

    async def add(self, course):
        self.items[course.id] = course


class EmptyRepository:
    async def get_by_ids(self, _):
        return []

    async def list_by_code_task_id(self, _):
        return []


class FakePublicationUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.courses = FakeCourseRepository()
        self.modules = EmptyRepository()
        self.sections = EmptyRepository()
        self.lectures = EmptyRepository()
        self.questions = EmptyRepository()
        self.answer_options = EmptyRepository()
        self.code_tasks = EmptyRepository()
        self.test_cases = EmptyRepository()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None


def make_author() -> User:
    return User(
        id=uuid4(),
        email="author@example.com",
        hashed_password="hashed-password",
        role=UserRole.AUTHOR,
    )


def make_course(author: User) -> Course:
    return Course(
        id=uuid4(),
        author_id=author.id,
        title="Course",
        description="Description",
    )


@pytest.mark.asyncio
async def test_publish_use_case_raises_error_for_not_ready_course() -> None:
    uow = FakePublicationUnitOfWork()
    actor = make_author()
    course = make_course(actor)
    await uow.courses.add(course)

    use_case = PublishCourseUseCase(uow=uow)

    with pytest.raises(CoursePublicationNotReadyError):
        await use_case.execute(
            PublishCourseCommand(
                actor=actor,
                course_id=course.id,
            )
        )

    assert uow.committed is False
