from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.section import Section
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateSectionCommand:
    actor: User
    section_id: UUID
    title: str
    description: str
    position: int


class UpdateSectionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.content_cache = content_cache

    async def execute(self, command: UpdateSectionCommand) -> Section:
        course_id: UUID | None = None
        async with self.uow:
            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=command.section_id,
            )

            section.update(
                title=command.title,
                description=command.description,
                position=command.position,
            )
            await self.uow.sections.update(section)
            await self.uow.commit()
            course_id = await self.course_access_service.resolve_course_id_for_section(
                section.id
            )

        if self.content_cache is not None and course_id is not None:
            await self.content_cache.invalidate_course(course_id)

        return section
