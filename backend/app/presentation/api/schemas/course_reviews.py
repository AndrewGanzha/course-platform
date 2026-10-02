from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UpsertCourseReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=1, max_length=2000)


class CourseReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID
    student_id: UUID
    rating: int
    text: str
