from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.course import Course, CourseDifficulty


class CourseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, course_id: UUID) -> Course | None:
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> "list[Course]":
        raise NotImplementedError

    @abstractmethod
    async def list_published(self) -> "list[Course]":
        raise NotImplementedError

    @abstractmethod
    async def find_published_catalog_courses(
        self,
        *,
        search: str = "",
        difficulty: CourseDifficulty | None = None,
    ) -> "list[Course]":
        raise NotImplementedError

    @abstractmethod
    async def add(self, course: Course) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, course: Course) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, course_id: UUID) -> None:
        raise NotImplementedError
