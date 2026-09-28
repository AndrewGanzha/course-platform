from app.application.dto.course_publication import (
    CoursePublicationIssueCode,
    CoursePublicationIssueDTO,
    CoursePublicationReadinessDTO,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.code_task import CodeTask
from app.domain.entities.course import Course
from app.domain.entities.question import Question
from app.domain.exceptions import InvalidQuestionError


class CoursePublicationReadinessService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def inspect_course(self, course: Course) -> CoursePublicationReadinessDTO:
        issues: list[CoursePublicationIssueDTO] = []

        modules = await self.uow.modules.get_by_ids(course.module_ids)
        if len(modules) == 0:
            issues.append(
                CoursePublicationIssueDTO(
                    code=CoursePublicationIssueCode.COURSE_WITHOUT_MODULES,
                    message="Course must contain at least one module before publication.",
                    entity_id=course.id,
                )
            )
            return CoursePublicationReadinessDTO(
                course_id=course.id,
                is_ready=False,
                issues=issues,
            )

        for module in sorted(modules, key=lambda item: item.position):
            if len(module.section_ids) == 0:
                issues.append(
                    CoursePublicationIssueDTO(
                        code=CoursePublicationIssueCode.MODULE_WITHOUT_SECTIONS,
                        message="Module must contain at least one section before publication.",
                        entity_id=module.id,
                    )
                )
                continue

            sections = await self.uow.sections.get_by_ids(module.section_ids)
            for section in sorted(sections, key=lambda item: item.position):
                await self._inspect_section(section, issues)

        return CoursePublicationReadinessDTO(
            course_id=course.id,
            is_ready=len(issues) == 0,
            issues=issues,
        )

    async def _inspect_section(
        self,
        section,
        issues: list[CoursePublicationIssueDTO],
    ) -> None:
        if len(section.lecture_ids) == 0:
            issues.append(
                CoursePublicationIssueDTO(
                    code=CoursePublicationIssueCode.SECTION_WITHOUT_LECTURES,
                    message="Section must contain at least one lecture before publication.",
                    entity_id=section.id,
                )
            )

        questions = await self.uow.questions.get_by_ids(section.question_ids)
        for question in questions:
            await self._inspect_question(question, issues)

        code_tasks = await self.uow.code_tasks.get_by_ids(section.code_task_ids)
        for code_task in code_tasks:
            await self._inspect_code_task(code_task, issues)

    async def _inspect_question(
        self,
        question: Question,
        issues: list[CoursePublicationIssueDTO],
    ) -> None:
        answer_options = await self.uow.answer_options.get_by_ids(
            question.answer_option_ids
        )
        try:
            question.validate_answer_options_configuration(answer_options)
        except InvalidQuestionError as exc:
            issues.append(
                CoursePublicationIssueDTO(
                    code=CoursePublicationIssueCode.QUESTION_WITH_INVALID_OPTIONS,
                    message=str(exc),
                    entity_id=question.id,
                )
            )

    async def _inspect_code_task(
        self,
        code_task: CodeTask,
        issues: list[CoursePublicationIssueDTO],
    ) -> None:
        test_cases = await self.uow.test_cases.list_by_code_task_id(code_task.id)
        if len(test_cases) == 0:
            issues.append(
                CoursePublicationIssueDTO(
                    code=CoursePublicationIssueCode.CODE_TASK_WITHOUT_TEST_CASES,
                    message="CodeTask must contain at least one test case before publication.",
                    entity_id=code_task.id,
                )
            )
