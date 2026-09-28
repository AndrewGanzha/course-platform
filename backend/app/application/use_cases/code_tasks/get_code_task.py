from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CodeTaskNotFoundError
from app.application.interfaces.repositories.code_task_repository import (
    CodeTaskRepository,
)
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.code_task import CodeTask
from app.domain.entities.user import User


@dataclass(slots=True)
class GetCodeTaskQuery:
    code_task_id: UUID
    actor: User | None = None


class GetCodeTaskUseCase:
    def __init__(
        self,
        code_task_repository: CodeTaskRepository,
        access_service: CourseContentAccessService,
    ) -> None:
        self.code_task_repository = code_task_repository
        self.access_service = access_service

    async def execute(self, query: GetCodeTaskQuery) -> CodeTask:
        code_task = await self.code_task_repository.get_by_id(query.code_task_id)
        if code_task is None:
            raise CodeTaskNotFoundError("CodeTask not found.")

        can_view = await self.access_service.can_view_section_content(
            section_id=code_task.section_id,
            actor=query.actor,
        )
        if not can_view:
            raise CodeTaskNotFoundError("CodeTask not found.")

        return code_task
