from pathlib import Path
from uuid import uuid4

import pytest

from app.application.exceptions import (
    CourseNotFoundError,
    InvalidCoverImageError,
    PermissionDeniedError,
)
from app.application.interfaces.storage.image_storage import ImageStorage
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.cover_image_policy import CoverImagePolicy
from app.application.use_cases.courses.upload_course_cover import (
    UploadCourseCoverCommand,
    UploadCourseCoverUseCase,
)
from app.domain.entities.course import Course
from app.domain.entities.user import User, UserRole


class FakeCourseRepository:
    def __init__(self) -> None:
        self.items = {}
        self.updated_ids = []

    async def get_by_id(self, course_id):
        return self.items.get(course_id)

    async def list(self):
        return list(self.items.values())

    async def add(self, course) -> None:
        self.items[course.id] = course

    async def update(self, course) -> None:
        self.updated_ids.append(course.id)
        self.items[course.id] = course

    async def remove(self, course_id) -> None:
        self.items.pop(course_id, None)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.courses = FakeCourseRepository()
        self.committed = False
        self.commit_count = 0
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeImageStorage(ImageStorage):
    def __init__(self) -> None:
        self.saved = []

    async def save(self, *, course_id, filename, content) -> str:
        self.saved.append((course_id, filename, content))
        extension = Path(filename).suffix.lower()
        return f"/media/course-covers/{course_id}/stored{extension}"


def make_author() -> User:
    return User(
        id=uuid4(),
        email="author@example.com",
        hashed_password="hashed-password",
        role=UserRole.AUTHOR,
    )


def make_course(actor: User) -> Course:
    return Course(
        id=uuid4(),
        author_id=actor.id,
        title="Course",
        description="Description",
    )


def build_use_case(
    uow: FakeUnitOfWork,
    storage: FakeImageStorage,
    *,
    max_size_bytes: int = 1024,
) -> UploadCourseCoverUseCase:
    return UploadCourseCoverUseCase(
        uow=uow,
        image_storage=storage,
        cover_image_policy=CoverImagePolicy(max_size_bytes=max_size_bytes),
    )


@pytest.mark.asyncio
async def test_upload_sets_cover_and_commits() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_course(actor)
    await uow.courses.add(course)
    storage = FakeImageStorage()

    use_case = build_use_case(uow, storage)
    result = await use_case.execute(
        UploadCourseCoverCommand(
            actor=actor,
            course_id=course.id,
            filename="cover.png",
            content_type="image/png",
            content=b"image-bytes",
        )
    )

    assert result.cover_image_url == f"/media/course-covers/{course.id}/stored.png"
    assert storage.saved == [(course.id, "cover.png", b"image-bytes")]
    assert uow.committed is True


@pytest.mark.asyncio
async def test_upload_raises_not_found_when_course_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    storage = FakeImageStorage()

    use_case = build_use_case(uow, storage)
    with pytest.raises(CourseNotFoundError):
        await use_case.execute(
            UploadCourseCoverCommand(
                actor=actor,
                course_id=uuid4(),
                filename="cover.png",
                content_type="image/png",
                content=b"image-bytes",
            )
        )

    assert storage.saved == []
    assert uow.commit_count == 0


@pytest.mark.asyncio
async def test_upload_raises_permission_denied_for_foreign_course() -> None:
    uow = FakeUnitOfWork()
    owner = make_author()
    intruder = make_author()
    course = make_course(owner)
    await uow.courses.add(course)
    storage = FakeImageStorage()

    use_case = build_use_case(uow, storage)
    with pytest.raises(PermissionDeniedError):
        await use_case.execute(
            UploadCourseCoverCommand(
                actor=intruder,
                course_id=course.id,
                filename="cover.png",
                content_type="image/png",
                content=b"image-bytes",
            )
        )

    assert storage.saved == []
    assert uow.commit_count == 0


@pytest.mark.asyncio
async def test_upload_rejects_invalid_content_type_before_saving() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_course(actor)
    await uow.courses.add(course)
    storage = FakeImageStorage()

    use_case = build_use_case(uow, storage)
    with pytest.raises(InvalidCoverImageError):
        await use_case.execute(
            UploadCourseCoverCommand(
                actor=actor,
                course_id=course.id,
                filename="cover.png",
                content_type="text/plain",
                content=b"image-bytes",
            )
        )

    assert storage.saved == []
    assert uow.commit_count == 0


@pytest.mark.asyncio
async def test_upload_rejects_oversized_image() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_course(actor)
    await uow.courses.add(course)
    storage = FakeImageStorage()

    use_case = build_use_case(uow, storage, max_size_bytes=4)
    with pytest.raises(InvalidCoverImageError):
        await use_case.execute(
            UploadCourseCoverCommand(
                actor=actor,
                course_id=course.id,
                filename="cover.png",
                content_type="image/png",
                content=b"12345",
            )
        )

    assert storage.saved == []
    assert uow.commit_count == 0
