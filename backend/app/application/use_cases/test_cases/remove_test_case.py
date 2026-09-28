from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    CodeTaskAlreadyUsedError,
    CodeTaskNotFoundError,
    TestCaseNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User
from app.domain.exceptions import InvalidCodeTaskError


@dataclass(slots=True)
class RemoveTestCaseCommand:
    actor: User
    test_case_id: UUID


class RemoveTestCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: RemoveTestCaseCommand) -> None:
        async with self.uow:
            test_case = await self.uow.test_cases.get_by_id(command.test_case_id)
            if test_case is None:
                raise TestCaseNotFoundError("TestCase not found.")

            code_task = await self.uow.code_tasks.get_by_id(test_case.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError("CodeTask not found.")

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=code_task.section_id,
            )

            has_submissions = await self.uow.code_submissions.exists_by_code_task_id(
                code_task.id
            )
            try:
                code_task.ensure_test_cases_can_be_changed(has_submissions)
            except InvalidCodeTaskError as exc:
                raise CodeTaskAlreadyUsedError(str(exc)) from exc

            existing_test_cases = await self.uow.test_cases.list_by_code_task_id(
                code_task.id
            )
            code_task.test_case_ids = [item.id for item in existing_test_cases]
            code_task.remove_test_case(test_case.id)

            remaining_test_cases = [
                item for item in existing_test_cases if item.id != test_case.id
            ]
            code_task.validate_test_cases_configuration(remaining_test_cases)

            await self.uow.code_tasks.update(code_task)
            await self.uow.test_cases.remove(test_case.id)
            await self.uow.commit()
