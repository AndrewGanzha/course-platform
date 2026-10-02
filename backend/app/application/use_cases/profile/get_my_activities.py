from dataclasses import dataclass
from uuid import UUID

from app.application.dto.student_activities import (
    StudentActivityPageDTO,
    build_activity_page,
    normalize_limit,
)
from app.application.exceptions import PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.student_activity import StudentActivityType
from app.domain.entities.user import User


@dataclass(slots=True)
class GetMyActivitiesQuery:
    actor: User
    limit: int = 20
    offset: int = 0
    course_id: UUID | None = None
    activity_type: StudentActivityType | None = None


class GetMyActivitiesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, query: GetMyActivitiesQuery) -> StudentActivityPageDTO:
        if not query.actor.is_student():
            raise PermissionDeniedError("User cannot view own activity history.")

        limit = normalize_limit(query.limit)
        offset = max(0, query.offset)

        async with self.uow:
            activities = await self.uow.student_activities.list_activities(
                limit=limit,
                offset=offset,
                student_id=query.actor.id,
                course_id=query.course_id,
                activity_type=query.activity_type,
            )
            total = await self.uow.student_activities.count_activities(
                student_id=query.actor.id,
                course_id=query.course_id,
                activity_type=query.activity_type,
            )

        return build_activity_page(activities, total, limit, offset)
