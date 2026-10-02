from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities.course import CourseDifficulty, CourseStatus


class CourseCatalogCountersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    module_count: int
    section_count: int
    lecture_count: int
    question_count: int
    task_count: int
    code_task_count: int


class CourseRatingSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    average_rating: float
    reviews_count: int


class CourseCatalogItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    short_description: str
    cover_image_url: str | None
    difficulty: CourseDifficulty
    tag_names: list[str]
    status: CourseStatus
    counters: CourseCatalogCountersResponse
    rating: CourseRatingSummaryResponse


class CourseCatalogSectionPreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    position: int


class CourseCatalogModulePreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    position: int
    sections: list[CourseCatalogSectionPreviewResponse]


class CourseCatalogCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    short_description: str
    cover_image_url: str | None
    difficulty: CourseDifficulty
    tag_names: list[str]
    status: CourseStatus
    counters: CourseCatalogCountersResponse
    rating: CourseRatingSummaryResponse
    modules: list[CourseCatalogModulePreviewResponse]
