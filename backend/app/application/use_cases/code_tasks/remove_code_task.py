from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    CodeTaskAlreadyUsedError,
    CodeTaskNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User
from app.domain.exceptions import InvalidCodeTaskError


@dataclass(slots=True)
class RemoveCodeTaskCommand:
    actor: User
    code_task_id: UUID


class RemoveCodeTaskUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: RemoveCodeTaskCommand) -> None:
        async with self.uow:
            code_task = await self.uow.code_tasks.get_by_id(command.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError("CodeTask not found.")

            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=code_task.section_id,
            )

            has_submissions = await self.uow.code_submissions.exists_by_code_task_id(
                code_task.id
            )
            try:
                code_task.ensure_can_be_removed(has_submissions)
            except InvalidCodeTaskError as exc:
                raise CodeTaskAlreadyUsedError(str(exc)) from exc

            section.remove_code_task(code_task.id)
            await self.uow.sections.update(section)
            await self.uow.code_tasks.remove(code_task.id)
            await self.uow.commit()
