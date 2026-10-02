from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import LectureNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class RemoveLectureCommand:
    actor: User
    lecture_id: UUID


class RemoveLectureUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.content_cache = content_cache

    async def execute(self, command: RemoveLectureCommand) -> None:
        course_id: UUID | None = None
        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(command.lecture_id)

            if lecture is None:
                raise LectureNotFoundError("Lecture not found")

            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=lecture.section_id,
            )

            section.remove_lecture(lecture.id)
            await self.uow.sections.update(section)
            await self.uow.lectures.remove(command.lecture_id)
            await self.uow.commit()
            course_id = await self.course_access_service.resolve_course_id_for_section(
                section.id
            )

        if self.content_cache is not None and course_id is not None:
            await self.content_cache.invalidate_course(course_id)
