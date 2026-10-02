from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.student_activity_repository import (
    StudentActivityRepository,
)
from app.domain.entities.student_activity import StudentActivity, StudentActivityType
from app.infrastructure.database.mappers.student_activity_mapper import (
    StudentActivityMapper,
)
from app.infrastructure.database.models.student_activity_model import (
    StudentActivityModel,
)


class SqlAlchemyStudentActivityRepository(StudentActivityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, activity: StudentActivity) -> None:
        self.session.add(StudentActivityMapper.to_model(activity))
        await self.session.flush()

    async def list_by_student_id(
        self,
        student_id: UUID,
        limit: int,
        offset: int,
    ) -> list[StudentActivity]:
        return await self.list_activities(
            limit=limit,
            offset=offset,
            student_id=student_id,
        )

    async def count_by_student_id(self, student_id: UUID) -> int:
        return await self.count_activities(student_id=student_id)

    async def list_activities(
        self,
        limit: int,
        offset: int,
        student_id: UUID | None = None,
        course_id: UUID | None = None,
        course_ids: list[UUID] | None = None,
        activity_type: StudentActivityType | None = None,
    ) -> list[StudentActivity]:
        stmt = (
            select(StudentActivityModel)
            .where(
                *self._build_filters(
                    student_id=student_id,
                    course_id=course_id,
                    course_ids=course_ids,
                    activity_type=activity_type,
                )
            )
            .order_by(
                StudentActivityModel.occurred_at.desc(),
                StudentActivityModel.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [
            StudentActivityMapper.to_domain(model) for model in result.scalars().all()
        ]

    async def count_activities(
        self,
        student_id: UUID | None = None,
        course_id: UUID | None = None,
        course_ids: list[UUID] | None = None,
        activity_type: StudentActivityType | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(StudentActivityModel)
            .where(
                *self._build_filters(
                    student_id=student_id,
                    course_id=course_id,
                    course_ids=course_ids,
                    activity_type=activity_type,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _build_filters(
        student_id: UUID | None,
        course_id: UUID | None,
        course_ids: list[UUID] | None,
        activity_type: StudentActivityType | None,
    ) -> list:
        filters: list = []
        if student_id is not None:
            filters.append(StudentActivityModel.student_id == str(student_id))
        if course_id is not None:
            filters.append(StudentActivityModel.course_id == str(course_id))
        if course_ids is not None:
            filters.append(
                StudentActivityModel.course_id.in_([str(item) for item in course_ids])
            )
        if activity_type is not None:
            filters.append(StudentActivityModel.activity_type == activity_type.value)
        return filters
