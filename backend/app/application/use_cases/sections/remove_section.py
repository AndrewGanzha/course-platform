from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class RemoveSectionCommand:
    actor: User
    section_id: UUID


class RemoveSectionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: RemoveSectionCommand) -> None:
        async with self.uow:
            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=command.section_id,
            )
            module = await self.course_access_service.ensure_can_manage_module(
                actor=command.actor,
                module_id=section.module_id,
            )

            module.remove_section(section.id)
            await self.uow.modules.update(module)
            await self.uow.sections.remove(command.section_id)
            await self.uow.commit()
