from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.course_review_repository import (
    CourseReviewRepository,
)
from app.domain.entities.course_review import CourseReview
from app.infrastructure.database.mappers.course_review_mapper import CourseReviewMapper
from app.infrastructure.database.models.course_review_model import CourseReviewModel


class SqlAlchemyCourseReviewRepository(CourseReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, review_id: UUID) -> CourseReview | None:
        model = await self.session.get(CourseReviewModel, str(review_id))
        return None if model is None else CourseReviewMapper.to_domain(model)

    async def get_by_student_and_course(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> CourseReview | None:
        stmt = select(CourseReviewModel).where(
            CourseReviewModel.student_id == str(student_id),
            CourseReviewModel.course_id == str(course_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else CourseReviewMapper.to_domain(model)

    async def list_by_course_id(self, course_id: UUID) -> list[CourseReview]:
        stmt = select(CourseReviewModel).where(
            CourseReviewModel.course_id == str(course_id)
        )
        result = await self.session.execute(stmt)
        return [CourseReviewMapper.to_domain(model) for model in result.scalars().all()]

    async def add(self, review: CourseReview) -> None:
        self.session.add(CourseReviewMapper.to_model(review))
        await self.session.flush()

    async def update(self, review: CourseReview) -> None:
        model = await self.session.get(CourseReviewModel, str(review.id))
        if model is None:
            return
        model.rating = review.rating
        model.text = review.text
        await self.session.flush()
