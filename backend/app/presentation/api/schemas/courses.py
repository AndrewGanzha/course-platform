from pydantic import BaseModel, Field, HttpUrl

from app.domain.entities.course import CourseDifficulty


class CourseWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    short_description: str = Field(default="", max_length=280)
    cover_image_url: HttpUrl | None = None
    difficulty: CourseDifficulty = CourseDifficulty.BEGINNER
    tag_names: list[str] = Field(default_factory=list, max_length=10)


class CreateCourseRequest(CourseWriteRequest):
    pass


class UpdateCourseRequest(CourseWriteRequest):
    pass
