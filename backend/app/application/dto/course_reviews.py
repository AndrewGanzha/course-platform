from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CourseReviewDTO:
    id: UUID
    course_id: UUID
    student_id: UUID
    rating: int
    text: str


@dataclass(slots=True)
class CourseRatingSummaryDTO:
    average_rating: float
    reviews_count: int
