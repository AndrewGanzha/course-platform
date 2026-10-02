from uuid import UUID

from app.application.dto.course_reviews import CourseRatingSummaryDTO
from app.application.interfaces.repositories.course_review_repository import (
    CourseReviewRepository,
)


class CourseRatingReadService:
    def __init__(self, review_repository: CourseReviewRepository) -> None:
        self.review_repository = review_repository

    async def build_summary(self, course_id: UUID) -> CourseRatingSummaryDTO:
        reviews = await self.review_repository.list_by_course_id(course_id)
        if not reviews:
            return CourseRatingSummaryDTO(
                average_rating=0.0,
                reviews_count=0,
            )

        return CourseRatingSummaryDTO(
            average_rating=sum(review.rating for review in reviews) / len(reviews),
            reviews_count=len(reviews),
        )
