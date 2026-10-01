from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StudentModuleAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    module_id: UUID
    title: str
    completed_sections_count: int
    total_sections_count: int
    is_completed: bool


class StudentWeakQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: UUID
    section_id: UUID
    attempts_count: int


class StudentWeakTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    section_id: UUID
    attempts_count: int


class StudentCourseAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: UUID
    course_title: str
    completion_ratio: float
    is_completed: bool
    total_points: int
    completed_modules_count: int
    total_modules_count: int
    completed_sections_count: int
    total_sections_count: int
    modules: list[StudentModuleAnalyticsResponse]
    weak_questions: list[StudentWeakQuestionResponse]
    weak_tasks: list[StudentWeakTaskResponse]
