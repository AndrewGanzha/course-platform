from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.student_activity import StudentActivity, StudentActivityType


class StudentActivityRepository(ABC):
    @abstractmethod
    async def add(self, activity: StudentActivity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_student_id(
        self,
        student_id: UUID,
        limit: int,
        offset: int,
    ) -> list[StudentActivity]:
        raise NotImplementedError

    @abstractmethod
    async def count_by_student_id(self, student_id: UUID) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list_activities(
        self,
        limit: int,
        offset: int,
        student_id: UUID | None = None,
        course_id: UUID | None = None,
        course_ids: list[UUID] | None = None,
        activity_type: StudentActivityType | None = None,
    ) -> list[StudentActivity]:
        raise NotImplementedError

    @abstractmethod
    async def count_activities(
        self,
        student_id: UUID | None = None,
        course_id: UUID | None = None,
        course_ids: list[UUID] | None = None,
        activity_type: StudentActivityType | None = None,
    ) -> int:
        raise NotImplementedError
