from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class RemoveCourseCommand:
    actor: User
    course_id: UUID


class RemoveCourseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.content_cache = content_cache

    async def execute(self, command: RemoveCourseCommand) -> None:
        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=command.actor,
                course_id=command.course_id,
            )
            await self.uow.courses.remove(course.id)
            await self.uow.commit()

        if self.content_cache is not None:
            await self.content_cache.invalidate_course(command.course_id)
