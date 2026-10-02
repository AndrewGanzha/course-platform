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
class GetAuthorActivitiesQuery:
    actor: User
    limit: int = 20
    offset: int = 0
    student_id: UUID | None = None
    course_id: UUID | None = None
    activity_type: StudentActivityType | None = None


class GetAuthorActivitiesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, query: GetAuthorActivitiesQuery) -> StudentActivityPageDTO:
        if not query.actor.is_author():
            raise PermissionDeniedError("Author access is required.")

        limit = normalize_limit(query.limit)
        offset = max(0, query.offset)

        async with self.uow:
            owned_courses = [
                course
                for course in await self.uow.courses.list()
                if course.is_owned_by(query.actor.id)
            ]
            owned_course_ids = [course.id for course in owned_courses]

            if query.course_id is not None:
                if query.course_id not in owned_course_ids:
                    raise PermissionDeniedError(
                        "Author cannot view activity of this course."
                    )
                course_ids = [query.course_id]
            else:
                course_ids = owned_course_ids

            if not course_ids:
                return build_activity_page([], 0, limit, offset)

            activities = await self.uow.student_activities.list_activities(
                limit=limit,
                offset=offset,
                student_id=query.student_id,
                course_ids=course_ids,
                activity_type=query.activity_type,
            )
            total = await self.uow.student_activities.count_activities(
                student_id=query.student_id,
                course_ids=course_ids,
                activity_type=query.activity_type,
            )

        return build_activity_page(activities, total, limit, offset)
