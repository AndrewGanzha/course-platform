from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CoursePublicationNotReadyError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.application.services.course_publication_readiness_service import (
    CoursePublicationReadinessService,
)
from app.domain.entities.course import Course
from app.domain.entities.user import User


@dataclass(slots=True)
class PublishCourseCommand:
    actor: User
    course_id: UUID


class PublishCourseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.course_publication_readiness_service = CoursePublicationReadinessService(
            uow
        )
        self.content_cache = content_cache

    async def execute(self, command: PublishCourseCommand) -> Course:
        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=command.actor,
                course_id=command.course_id,
            )
            readiness = await self.course_publication_readiness_service.inspect_course(
                course
            )
            if not readiness.is_ready:
                raise CoursePublicationNotReadyError(readiness)

            course.publish()
            await self.uow.courses.update(course)
            await self.uow.commit()

        if self.content_cache is not None:
            await self.content_cache.invalidate_course(command.course_id)

        return course
