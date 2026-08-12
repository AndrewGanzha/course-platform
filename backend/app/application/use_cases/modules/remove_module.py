from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class RemoveModuleCommand:
    actor: User
    module_id: UUID


class RemoveModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: RemoveModuleCommand) -> None:
        async with self.uow:
            module = await self.course_access_service.ensure_can_manage_module(
                actor=command.actor,
                module_id=command.module_id,
            )
            course = await self.course_access_service.ensure_can_manage_course(
                actor=command.actor,
                course_id=module.course_id,
            )

            course.remove_module(module.id)
            await self.uow.courses.update(course)
            await self.uow.modules.remove(command.module_id)
            await self.uow.commit()
