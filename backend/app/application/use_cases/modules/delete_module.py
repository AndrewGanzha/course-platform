from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.exceptions import ModuleNotFoundError


@dataclass(slots=True)
class DeleteModuleCommand:
    module_id: UUID


class DeleteModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: DeleteModuleCommand) -> None:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)

            if module is None:
                raise ModuleNotFoundError("Module not found")

            await self.uow.modules.delete(command.module_id)
            await self.uow.commit()