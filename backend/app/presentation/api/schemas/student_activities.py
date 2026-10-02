from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities.student_activity import StudentActivityType


class StudentActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    course_id: UUID
    activity_type: StudentActivityType
    entity_id: UUID
    title: str
    details: dict[str, str | int | float | bool]
    occurred_at: datetime


class StudentActivityPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[StudentActivityResponse]
    total: int
    limit: int
    offset: int
