import pickle
from uuid import UUID

from redis.asyncio import Redis

from app.application.dto.student_course_analytics import (
    StudentCourseAnalyticsDTO,
)
from app.application.interfaces.student_analytics_cache import (
    StudentAnalyticsCache,
)


class RedisStudentAnalyticsCache(StudentAnalyticsCache):
    def __init__(
        self,
        client: Redis,
        ttl_seconds: int,
    ) -> None:
        self.client = client
        self.ttl_seconds = ttl_seconds

    def _key(self, student_id: UUID, course_id: UUID) -> str:
        return f"analytics:student:{student_id}:course:{course_id}"

    async def get(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> StudentCourseAnalyticsDTO | None:
        value = await self.client.get(self._key(student_id, course_id))
        if value is None:
            return None
        return pickle.loads(value)

    async def set(
        self,
        student_id: UUID,
        course_id: UUID,
        value: StudentCourseAnalyticsDTO,
    ) -> None:
        await self.client.set(
            self._key(student_id, course_id),
            pickle.dumps(value),
            ex=self.ttl_seconds,
        )

    async def invalidate_student_course(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> None:
        await self.client.delete(self._key(student_id, course_id))
