from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import TaskAlreadyUsedError, TaskNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User
from app.domain.exceptions import InvalidTaskError


@dataclass(slots=True)
class RemoveTaskCommand:
    actor: User
    task_id: UUID


class RemoveTaskUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: RemoveTaskCommand) -> None:
        async with self.uow:
            task = await self.uow.tasks.get_by_id(command.task_id)
            if task is None:
                raise TaskNotFoundError("Task not found.")

            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=task.section_id,
            )

            has_attempts = await self.uow.task_attempts.exists_by_task_id(task.id)
            try:
                task.ensure_can_be_removed(has_attempts)
            except InvalidTaskError as exc:
                raise TaskAlreadyUsedError(str(exc)) from exc

            section.remove_task(task.id)
            await self.uow.sections.update(section)
            await self.uow.tasks.remove(task.id)
            await self.uow.commit()
