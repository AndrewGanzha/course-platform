from dataclasses import dataclass
from uuid import UUID

from app.application.dto.course_publication import CoursePublicationReadinessDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.application.services.course_publication_readiness_service import (
    CoursePublicationReadinessService,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class GetCoursePublicationReadinessQuery:
    actor: User
    course_id: UUID


class GetCoursePublicationReadinessUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.course_publication_readiness_service = CoursePublicationReadinessService(
            uow
        )

    async def execute(
        self,
        query: GetCoursePublicationReadinessQuery,
    ) -> CoursePublicationReadinessDTO:
        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=query.actor,
                course_id=query.course_id,
            )
            return await self.course_publication_readiness_service.inspect_course(
                course
            )
