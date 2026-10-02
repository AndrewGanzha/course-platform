from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class AuthorModuleAnalyticsDTO:
    module_id: UUID
    title: str
    students_completed_count: int
    total_sections_count: int


@dataclass(slots=True)
class DifficultQuestionAnalyticsDTO:
    question_id: UUID
    section_id: UUID
    text: str
    students_count: int
    attempts_count: int
    first_try_success_rate: float
    average_attempts_per_student: float


@dataclass(slots=True)
class DifficultTaskAnalyticsDTO:
    task_id: UUID
    section_id: UUID
    title: str
    students_count: int
    attempts_count: int
    first_try_success_rate: float
    average_attempts_per_student: float


@dataclass(slots=True)
class ProblematicCodeTaskAnalyticsDTO:
    code_task_id: UUID
    section_id: UUID
    title: str
    students_count: int
    submissions_count: int
    passed_students_count: int
    pass_rate: float
    repeat_students_count: int


@dataclass(slots=True)
class AuthorCourseAnalyticsDTO:
    course_id: UUID
    course_title: str
    students_started_count: int
    students_completed_count: int
    completion_rate: float
    average_completion_ratio: float
    average_points: float
    modules: list[AuthorModuleAnalyticsDTO] = field(default_factory=list)
    difficult_questions: list[DifficultQuestionAnalyticsDTO] = field(
        default_factory=list
    )
    difficult_tasks: list[DifficultTaskAnalyticsDTO] = field(default_factory=list)
    problematic_code_tasks: list[ProblematicCodeTaskAnalyticsDTO] = field(
        default_factory=list
    )
