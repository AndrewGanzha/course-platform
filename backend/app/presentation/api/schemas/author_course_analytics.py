from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuthorModuleAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    module_id: UUID
    title: str
    students_completed_count: int
    total_sections_count: int


class DifficultQuestionAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    question_id: UUID
    section_id: UUID
    text: str
    students_count: int
    attempts_count: int
    first_try_success_rate: float
    average_attempts_per_student: float


class DifficultTaskAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    task_id: UUID
    section_id: UUID
    title: str
    students_count: int
    attempts_count: int
    first_try_success_rate: float
    average_attempts_per_student: float


class ProblematicCodeTaskAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code_task_id: UUID
    section_id: UUID
    title: str
    students_count: int
    submissions_count: int
    passed_students_count: int
    pass_rate: float
    repeat_students_count: int


class AuthorCourseAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    course_id: UUID
    course_title: str
    students_started_count: int
    students_completed_count: int
    completion_rate: float
    average_completion_ratio: float
    average_points: float
    modules: list[AuthorModuleAnalyticsResponse]
    difficult_questions: list[DifficultQuestionAnalyticsResponse]
    difficult_tasks: list[DifficultTaskAnalyticsResponse]
    problematic_code_tasks: list[ProblematicCodeTaskAnalyticsResponse]
