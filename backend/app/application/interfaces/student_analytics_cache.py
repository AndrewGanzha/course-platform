from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dto.student_course_analytics import (
    StudentCourseAnalyticsDTO,
)


class StudentAnalyticsCache(ABC):
    @abstractmethod
    async def get(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> StudentCourseAnalyticsDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def set(
        self,
        student_id: UUID,
        course_id: UUID,
        value: StudentCourseAnalyticsDTO,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def invalidate_student_course(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> None:
        raise NotImplementedError
