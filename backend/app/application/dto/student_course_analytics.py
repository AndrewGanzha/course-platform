from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class StudentModuleAnalyticsDTO:
    module_id: UUID
    title: str
    completed_sections_count: int
    total_sections_count: int
    is_completed: bool


@dataclass(slots=True)
class StudentWeakQuestionDTO:
    question_id: UUID
    section_id: UUID
    attempts_count: int


@dataclass(slots=True)
class StudentWeakTaskDTO:
    task_id: UUID
    section_id: UUID
    attempts_count: int


@dataclass(slots=True)
class StudentWeakCodeTaskDTO:
    code_task_id: UUID
    section_id: UUID
    attempts_count: int


@dataclass(slots=True)
class StudentCourseAnalyticsDTO:
    course_id: UUID
    course_title: str
    completion_ratio: float
    is_completed: bool
    total_points: int
    completed_modules_count: int
    total_modules_count: int
    completed_sections_count: int
    total_sections_count: int
    modules: list[StudentModuleAnalyticsDTO] = field(default_factory=list)
    weak_questions: list[StudentWeakQuestionDTO] = field(default_factory=list)
    weak_tasks: list[StudentWeakTaskDTO] = field(default_factory=list)
    weak_code_tasks: list[StudentWeakCodeTaskDTO] = field(default_factory=list)
