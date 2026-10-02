from datetime import UTC
from uuid import UUID

from app.domain.entities.student_activity import (
    StudentActivity,
    StudentActivityType,
)
from app.infrastructure.database.models.student_activity_model import (
    StudentActivityModel,
)


class StudentActivityMapper:
    @staticmethod
    def to_domain(model: StudentActivityModel) -> StudentActivity:
        return StudentActivity(
            id=UUID(model.id),
            student_id=UUID(model.student_id),
            course_id=UUID(model.course_id),
            activity_type=StudentActivityType(model.activity_type),
            entity_id=UUID(model.entity_id),
            title=model.title,
            details=dict(model.details),
            occurred_at=(
                model.occurred_at
                if model.occurred_at.tzinfo is not None
                else model.occurred_at.replace(tzinfo=UTC)
            ),
        )

    @staticmethod
    def to_model(activity: StudentActivity) -> StudentActivityModel:
        return StudentActivityModel(
            id=str(activity.id),
            student_id=str(activity.student_id),
            course_id=str(activity.course_id),
            activity_type=activity.activity_type.value,
            entity_id=str(activity.entity_id),
            title=activity.title,
            details=dict(activity.details),
            occurred_at=activity.occurred_at,
        )
