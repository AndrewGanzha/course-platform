from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import TaskNotFoundError
from app.application.interfaces.repositories.task_repository import TaskRepository
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.task import Task
from app.domain.entities.user import User


@dataclass(slots=True)
class GetTaskQuery:
    task_id: UUID
    actor: User | None = None


class GetTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepository,
        access_service: CourseContentAccessService,
    ) -> None:
        self.task_repository = task_repository
        self.access_service = access_service

    async def execute(self, query: GetTaskQuery) -> Task:
        task = await self.task_repository.get_by_id(query.task_id)
        if task is None:
            raise TaskNotFoundError("Task not found.")

        can_view = await self.access_service.can_view_section_content(
            section_id=task.section_id,
            actor=query.actor,
        )
        if not can_view:
            raise TaskNotFoundError("Task not found.")

        return task
