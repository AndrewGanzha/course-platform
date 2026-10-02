from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.course_review import CourseReview


class CourseReviewRepository(ABC):
    @abstractmethod
    async def get_by_id(self, review_id: UUID) -> CourseReview | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_student_and_course(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> CourseReview | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_course_id(self, course_id: UUID) -> list[CourseReview]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, review: CourseReview) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, review: CourseReview) -> None:
        raise NotImplementedError
