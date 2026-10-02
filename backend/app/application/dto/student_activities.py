from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.student_activity import StudentActivity, StudentActivityType

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@dataclass(slots=True)
class StudentActivityDTO:
    id: UUID
    student_id: UUID
    course_id: UUID
    activity_type: StudentActivityType
    entity_id: UUID
    title: str
    details: dict[str, str | int | float | bool]
    occurred_at: datetime


@dataclass(slots=True)
class StudentActivityPageDTO:
    items: list[StudentActivityDTO]
    total: int
    limit: int
    offset: int


def normalize_limit(limit: int) -> int:
    if limit < 1:
        return DEFAULT_LIMIT
    return min(limit, MAX_LIMIT)


def build_activity_dto(activity: StudentActivity) -> StudentActivityDTO:
    return StudentActivityDTO(
        id=activity.id,
        student_id=activity.student_id,
        course_id=activity.course_id,
        activity_type=activity.activity_type,
        entity_id=activity.entity_id,
        title=activity.title,
        details=activity.details,
        occurred_at=activity.occurred_at,
    )


def build_activity_page(
    activities: list[StudentActivity],
    total: int,
    limit: int,
    offset: int,
) -> StudentActivityPageDTO:
    return StudentActivityPageDTO(
        items=[build_activity_dto(activity) for activity in activities],
        total=total,
        limit=limit,
        offset=offset,
    )
