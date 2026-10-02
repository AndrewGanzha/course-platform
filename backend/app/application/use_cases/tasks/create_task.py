from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.task import Task, TaskCheckType
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateTaskCommand:
    actor: User
    section_id: UUID
    title: str
    statement: str
    position: int
    check_type: TaskCheckType
    expected_answer: str = ""
    accepted_answers: list[str] | None = None
    answer_pattern: str = ""
    max_attempts: int = 1
    reward_points: int = 1


class CreateTaskUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.content_cache = content_cache

    async def execute(self, command: CreateTaskCommand) -> Task:
        course_id: UUID | None = None
        async with self.uow:
            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=command.section_id,
            )

            task = Task(
                id=uuid4(),
                section_id=section.id,
                title=command.title,
                statement=command.statement,
                position=command.position,
                check_type=command.check_type,
                expected_answer=command.expected_answer,
                accepted_answers=command.accepted_answers or [],
                answer_pattern=command.answer_pattern,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
            )

            section.add_task(task.id)
            await self.uow.tasks.add(task)
            await self.uow.sections.update(section)
            await self.uow.commit()
            course_id = await self.course_access_service.resolve_course_id_for_section(
                section.id
            )

        if self.content_cache is not None and course_id is not None:
            await self.content_cache.invalidate_course(course_id)

        return task
