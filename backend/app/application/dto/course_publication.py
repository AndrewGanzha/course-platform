from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID


class CoursePublicationIssueCode(StrEnum):
    COURSE_WITHOUT_MODULES = "course_without_modules"
    MODULE_WITHOUT_SECTIONS = "module_without_sections"
    SECTION_WITHOUT_LECTURES = "section_without_lectures"
    QUESTION_WITH_INVALID_OPTIONS = "question_with_invalid_options"
    CODE_TASK_WITHOUT_TEST_CASES = "code_task_without_test_cases"


@dataclass(slots=True)
class CoursePublicationIssueDTO:
    code: CoursePublicationIssueCode
    message: str
    entity_id: UUID | None = None


@dataclass(slots=True)
class CoursePublicationReadinessDTO:
    course_id: UUID
    is_ready: bool
    issues: list[CoursePublicationIssueDTO] = field(default_factory=list)
