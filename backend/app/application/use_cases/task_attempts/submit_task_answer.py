from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import (
    ModuleNotFoundError,
    PermissionDeniedError,
    SectionNotFoundError,
    TaskNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.progress import Progress
from app.domain.entities.task_attempt import TaskAttempt
from app.domain.entities.user import User


@dataclass(slots=True)
class SubmitTaskAnswerCommand:
    actor: User
    task_id: UUID
    submitted_answer: str

class SubmitTaskAnswerUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: SubmitTaskAnswerCommand) -> TaskAttempt:
        if not command.actor.can_submit_task_solutions():
            raise PermissionDeniedError('User cannot submit task solutions.')

        async with self.uow:
            task = await self.uow.tasks.get_by_id(command.task_id)
            if task is None:
                raise TaskNotFoundError('Task not found.')

            attempts = await self.uow.task_attempts.list_by_task_id(task.id)
            student_attempts = [
                attempt
                for attempt in attempts
                if attempt.student_id == command.actor.id
            ]
            existing_attempts_count = len(student_attempts)
            has_correct_attempt = any(attempt.is_correct() for attempt in student_attempts)

            attempt = task.create_attempt(
                student_id=command.actor.id,
                submitted_answer=command.submitted_answer,
                existing_attempts_count=existing_attempts_count,
                has_correct_attempt=has_correct_attempt,
            )
            task.check_attempt(attempt)

            await self.uow.task_attempts.add(attempt)

            if attempt.is_correct():
                section = await self.uow.sections.get_by_id(task.section_id)
                if section is None:
                    raise SectionNotFoundError('Section not found.')

                module = await self.uow.modules.get_by_id(section.module_id)
                if module is None:
                    raise ModuleNotFoundError('Module not found.')

                progress = await self.uow.progress.get_by_student_and_course(
                    student_id=command.actor.id,
                    course_id=module.course_id,
                )

                progress_is_new = progress is None
                if progress is None:
                    progress = Progress(
                        id=uuid4(),
                        student_id=command.actor.id,
                        course_id=module.course_id,
                    )

                progress_changed = progress.apply_correct_task_attempt(attempt)
                if progress_changed:
                    progress.sync_section_completion(section)
                    progress.sync_module_completion(module)

                    if progress_is_new:
                        await self.uow.progress.add(progress)
                    else:
                        await self.uow.progress.update(progress)

            await self.uow.commit()
            return attempt