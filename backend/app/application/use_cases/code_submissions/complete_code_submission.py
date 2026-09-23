from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CodeSubmissionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.execution_result import ExecutionResult, ExecutionStatus


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
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

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
            await self.uow.commit()
            return submission
