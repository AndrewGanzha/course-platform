from uuid import UUID

from app.domain.entities.course_review import CourseReview
from app.infrastructure.database.models.course_review_model import CourseReviewModel


class CourseReviewMapper:
    @staticmethod
    def to_domain(model: CourseReviewModel) -> CourseReview:
        return CourseReview(
            id=UUID(model.id),
            course_id=UUID(model.course_id),
            student_id=UUID(model.student_id),
            rating=model.rating,
            text=model.text,
        )

    @staticmethod
    def to_model(review: CourseReview) -> CourseReviewModel:
        return CourseReviewModel(
            id=str(review.id),
            course_id=str(review.course_id),
            student_id=str(review.student_id),
            rating=review.rating,
            text=review.text,
        )
