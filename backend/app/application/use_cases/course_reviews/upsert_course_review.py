from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.dto.course_reviews import CourseReviewDTO
from app.application.exceptions import CourseNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.course_review import CourseReview
from app.domain.entities.student_activity import (
    StudentActivity,
    StudentActivityType,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class UpsertCourseReviewCommand:
    actor: User
    course_id: UUID
    rating: int
    text: str


class UpsertCourseReviewUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpsertCourseReviewCommand) -> CourseReviewDTO:
        if not command.actor.is_student():
            raise PermissionDeniedError("Only students can leave course reviews.")

        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None or not course.is_publicly_visible():
                raise CourseNotFoundError("Course not found.")

            progress = await self.uow.progress.get_by_student_and_course(
                student_id=command.actor.id,
                course_id=course.id,
            )
            if progress is None:
                raise PermissionDeniedError(
                    "At least 80% of the course must be completed before leaving a review."
                )

            modules = await self.uow.modules.get_by_ids(course.module_ids)
            total_sections_count = 0
            for module in modules:
                sections = await self.uow.sections.get_by_ids(module.section_ids)
                total_sections_count += len(sections)

            completion_ratio = progress.course_completion_ratio(total_sections_count)
            if completion_ratio < 0.8:
                raise PermissionDeniedError(
                    "At least 80% of the course must be completed before leaving a review."
                )

            review = await self.uow.course_reviews.get_by_student_and_course(
                student_id=command.actor.id,
                course_id=course.id,
            )

            if review is None:
                review = CourseReview(
                    id=uuid4(),
                    course_id=course.id,
                    student_id=command.actor.id,
                    rating=command.rating,
                    text=command.text,
                )
                await self.uow.course_reviews.add(review)
                activity_type = StudentActivityType.COURSE_REVIEW_CREATED
            else:
                review.update(rating=command.rating, text=command.text)
                await self.uow.course_reviews.update(review)
                activity_type = StudentActivityType.COURSE_REVIEW_UPDATED

            await self.uow.student_activities.add(
                StudentActivity(
                    id=uuid4(),
                    student_id=command.actor.id,
                    course_id=course.id,
                    activity_type=activity_type,
                    entity_id=review.id,
                    title=course.title,
                    details={"rating": review.rating},
                )
            )

            await self.uow.commit()
            return CourseReviewDTO(
                id=review.id,
                course_id=review.course_id,
                student_id=review.student_id,
                rating=review.rating,
                text=review.text,
            )
