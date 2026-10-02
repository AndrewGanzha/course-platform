from dataclasses import dataclass
from uuid import UUID

from app.application.dto.course_reviews import CourseReviewDTO
from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork


@dataclass(slots=True)
class GetCourseReviewsQuery:
    course_id: UUID


class GetCourseReviewsUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, query: GetCourseReviewsQuery) -> list[CourseReviewDTO]:
        async with self.uow:
            course = await self.uow.courses.get_by_id(query.course_id)
            if course is None or not course.is_publicly_visible():
                raise CourseNotFoundError("Course not found.")

            reviews = await self.uow.course_reviews.list_by_course_id(course.id)
            return [
                CourseReviewDTO(
                    id=review.id,
                    course_id=review.course_id,
                    student_id=review.student_id,
                    rating=review.rating,
                    text=review.text,
                )
                for review in reviews
            ]
