from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions import InvalidCourseReviewError


@dataclass(slots=True)
class CourseReview:
    id: UUID
    course_id: UUID
    student_id: UUID
    rating: int
    text: str

    def __post_init__(self) -> None:
        self.text = self.text.strip()
        self._validate()

    def _validate(self) -> None:
        if self.rating < 1 or self.rating > 5:
            raise InvalidCourseReviewError(
                "Course review rating must be between 1 and 5."
            )
        if not self.text:
            raise InvalidCourseReviewError("Course review text cannot be empty.")
        if len(self.text) > 2000:
            raise InvalidCourseReviewError(
                "Course review text cannot be longer than 2000 characters."
            )

    def update(self, *, rating: int, text: str) -> None:
        self.rating = rating
        self.text = text.strip()
        self._validate()

    def is_written_by(self, student_id: UUID) -> bool:
        return self.student_id == student_id
