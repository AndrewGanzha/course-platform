from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.module import Module
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateModuleCommand:
    actor: User
    module_id: UUID
    title: str
    description: str
    position: int


class UpdateModuleUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.content_cache = content_cache

    async def execute(self, command: UpdateModuleCommand) -> Module:
        course_id: UUID | None = None
        async with self.uow:
            module = await self.course_access_service.ensure_can_manage_module(
                actor=command.actor,
                module_id=command.module_id,
            )

            module.update(
                title=command.title,
                description=command.description,
                position=command.position,
            )
            await self.uow.modules.update(module)
            await self.uow.commit()
            course_id = module.course_id

        if self.content_cache is not None and course_id is not None:
            await self.content_cache.invalidate_course(course_id)

        return module
