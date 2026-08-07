from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CourseNotFoundError, ModuleNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork


@dataclass(slots=True)
class RemoveModuleCommand:
    module_id: UUID


class RemoveModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: RemoveModuleCommand) -> None:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)

            if module is None:
                raise ModuleNotFoundError("Module not found")

            course = await self.uow.courses.get_by_id(module.course_id)

            if course is None:
                raise CourseNotFoundError("Course not found")

            course.remove_module(module.id)
            await self.uow.courses.update(course)
            await self.uow.modules.remove(command.module_id)
            await self.uow.commit()
