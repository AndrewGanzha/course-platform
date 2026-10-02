from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidStudentActivityError


class StudentActivityType(StrEnum):
    QUESTION_COMPLETED = "question_completed"
    TASK_COMPLETED = "task_completed"
    CODE_TASK_COMPLETED = "code_task_completed"
    SECTION_COMPLETED = "section_completed"
    MODULE_COMPLETED = "module_completed"
    COURSE_REVIEW_CREATED = "course_review_created"
    COURSE_REVIEW_UPDATED = "course_review_updated"


@dataclass(slots=True)
class StudentActivity:
    id: UUID
    student_id: UUID
    course_id: UUID
    activity_type: StudentActivityType
    entity_id: UUID
    title: str
    details: dict[str, str | int | float | bool] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise InvalidStudentActivityError("Student activity title cannot be empty.")
        if self.occurred_at.tzinfo is None:
            raise InvalidStudentActivityError(
                "Student activity occurred_at must be timezone-aware."
            )
