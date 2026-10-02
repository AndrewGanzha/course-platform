from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import (
    CodeSubmissionNotFoundError,
    CodeTaskNotFoundError,
    ModuleNotFoundError,
    SectionNotFoundError,
)
from app.application.interfaces.student_analytics_cache import (
    StudentAnalyticsCache,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.execution_result import ExecutionResult, ExecutionStatus
from app.domain.entities.progress import Progress
from app.domain.entities.student_activity import (
    StudentActivity,
    StudentActivityType,
)


@dataclass(slots=True)
class CompleteCodeSubmissionCommand:
    submission_id: UUID
    status: ExecutionStatus
    passed_test_cases: int = 0
    total_test_cases: int = 0
    stdout: str = ""
    stderr: str = ""
    error_message: str = ""
    exit_code: int | None = None


class CompleteCodeSubmissionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        analytics_cache: StudentAnalyticsCache | None = None,
    ) -> None:
        self.uow = uow
        self.analytics_cache = analytics_cache

    async def execute(self, command: CompleteCodeSubmissionCommand):
        async with self.uow:
            submission = await self.uow.code_submissions.get_by_id(
                command.submission_id
            )
            if submission is None:
                raise CodeSubmissionNotFoundError("CodeSubmission not found.")

            result = ExecutionResult(
                submission_id=submission.id,
                status=command.status,
                passed_test_cases=command.passed_test_cases,
                total_test_cases=command.total_test_cases,
                stdout=command.stdout,
                stderr=command.stderr,
                error_message=command.error_message,
                exit_code=command.exit_code,
            )

            if submission.status.value == "pending":
                submission.mark_running()

            submission.apply_execution_result(result)
            await self.uow.code_submissions.update(submission)

            affected_course_id = None
            if result.status.value == "passed":
                code_task = await self.uow.code_tasks.get_by_id(submission.code_task_id)
                if code_task is None:
                    raise CodeTaskNotFoundError("CodeTask not found.")

                section = await self.uow.sections.get_by_id(code_task.section_id)
                if section is None:
                    raise SectionNotFoundError("Section not found.")

                module = await self.uow.modules.get_by_id(section.module_id)
                if module is None:
                    raise ModuleNotFoundError("Module not found.")

                affected_course_id = module.course_id
                progress = await self.uow.progress.get_by_student_and_course(
                    student_id=submission.student_id,
                    course_id=module.course_id,
                )
                if progress is None:
                    progress = Progress(
                        id=uuid4(),
                        student_id=submission.student_id,
                        course_id=module.course_id,
                    )
                    await self.uow.progress.add(progress)

                code_task_completed = progress.complete_code_task(
                    code_task.id, code_task.reward_points
                )
                section_completed = progress.sync_section_completion(section)
                module_completed = progress.sync_module_completion(module)
                await self.uow.progress.update(progress)

                if code_task_completed:
                    await self.uow.student_activities.add(
                        StudentActivity(
                            id=uuid4(),
                            student_id=submission.student_id,
                            course_id=module.course_id,
                            activity_type=(StudentActivityType.CODE_TASK_COMPLETED),
                            entity_id=code_task.id,
                            title=code_task.title,
                            details={"awarded_points": code_task.reward_points},
                        )
                    )

                if section_completed:
                    await self.uow.student_activities.add(
                        StudentActivity(
                            id=uuid4(),
                            student_id=submission.student_id,
                            course_id=module.course_id,
                            activity_type=StudentActivityType.SECTION_COMPLETED,
                            entity_id=section.id,
                            title=section.title,
                        )
                    )

                if module_completed:
                    await self.uow.student_activities.add(
                        StudentActivity(
                            id=uuid4(),
                            student_id=submission.student_id,
                            course_id=module.course_id,
                            activity_type=StudentActivityType.MODULE_COMPLETED,
                            entity_id=module.id,
                            title=module.title,
                        )
                    )

            await self.uow.commit()
            if self.analytics_cache is not None and affected_course_id is not None:
                await self.analytics_cache.invalidate_student_course(
                    student_id=submission.student_id,
                    course_id=affected_course_id,
                )
            return submission
