from dataclasses import dataclass
from uuid import UUID

from app.application.dto.author_course_analytics import (
    AuthorCourseAnalyticsDTO,
    AuthorModuleAnalyticsDTO,
    DifficultQuestionAnalyticsDTO,
    DifficultTaskAnalyticsDTO,
    ProblematicCodeTaskAnalyticsDTO,
)
from app.application.exceptions import PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.code_submission import CodeSubmission, CodeSubmissionStatus
from app.domain.entities.question_attempt import QuestionAttempt
from app.domain.entities.task_attempt import TaskAttempt
from app.domain.entities.user import User


@dataclass(slots=True)
class GetMyTeachingCourseAnalyticsQuery:
    actor: User
    course_id: UUID


class GetMyTeachingCourseAnalyticsUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(
        self, query: GetMyTeachingCourseAnalyticsQuery
    ) -> AuthorCourseAnalyticsDTO:
        if not query.actor.can_view_all_learning_results():
            raise PermissionDeniedError("User cannot view teaching analytics.")

        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=query.actor,
                course_id=query.course_id,
            )
            progresses = await self.uow.progress.list_by_course_id(course.id)
            modules = await self.uow.modules.get_by_ids(course.module_ids)

            total_sections_count = 0
            module_dtos: list[AuthorModuleAnalyticsDTO] = []
            question_dtos: list[DifficultQuestionAnalyticsDTO] = []
            task_dtos: list[DifficultTaskAnalyticsDTO] = []
            code_task_dtos: list[ProblematicCodeTaskAnalyticsDTO] = []

            for module in sorted(modules, key=lambda item: item.position):
                sections = await self.uow.sections.get_by_ids(module.section_ids)
                total_sections_count += len(sections)
                students_completed_module_count = sum(
                    1
                    for progress in progresses
                    if progress.has_completed_module(module.id)
                )
                module_dtos.append(
                    AuthorModuleAnalyticsDTO(
                        module_id=module.id,
                        title=module.title,
                        students_completed_count=students_completed_module_count,
                        total_sections_count=len(sections),
                    )
                )

                for section in sorted(sections, key=lambda item: item.position):
                    questions = await self.uow.questions.get_by_ids(
                        section.question_ids
                    )
                    tasks = await self.uow.tasks.get_by_ids(section.task_ids)
                    code_tasks = await self.uow.code_tasks.get_by_ids(
                        section.code_task_ids
                    )

                    for question in questions:
                        attempts = await self.uow.question_attempts.list_by_question_id(
                            question.id
                        )
                        grouped = self._group_question_attempts(attempts)
                        if grouped:
                            first_try_success_students = sum(
                                1
                                for student_attempts in grouped.values()
                                if student_attempts[0].is_correct()
                            )
                            question_dtos.append(
                                DifficultQuestionAnalyticsDTO(
                                    question_id=question.id,
                                    section_id=section.id,
                                    text=question.text,
                                    students_count=len(grouped),
                                    attempts_count=len(attempts),
                                    first_try_success_rate=first_try_success_students
                                    / len(grouped),
                                    average_attempts_per_student=len(attempts)
                                    / len(grouped),
                                )
                            )

                    for task in tasks:
                        attempts = await self.uow.task_attempts.list_by_task_id(task.id)
                        grouped = self._group_task_attempts(attempts)
                        if grouped:
                            first_try_success_students = sum(
                                1
                                for student_attempts in grouped.values()
                                if student_attempts[0].is_correct()
                            )
                            task_dtos.append(
                                DifficultTaskAnalyticsDTO(
                                    task_id=task.id,
                                    section_id=section.id,
                                    title=task.title,
                                    students_count=len(grouped),
                                    attempts_count=len(attempts),
                                    first_try_success_rate=first_try_success_students
                                    / len(grouped),
                                    average_attempts_per_student=len(attempts)
                                    / len(grouped),
                                )
                            )

                    for code_task in code_tasks:
                        submissions = (
                            await self.uow.code_submissions.list_by_code_task_id(
                                code_task.id
                            )
                        )
                        grouped = self._group_code_submissions(submissions)
                        if grouped:
                            passed_students_count = sum(
                                1
                                for student_submissions in grouped.values()
                                if any(
                                    submission.status is CodeSubmissionStatus.PASSED
                                    for submission in student_submissions
                                )
                            )
                            repeat_students_count = sum(
                                1
                                for student_submissions in grouped.values()
                                if len(student_submissions) > 1
                            )
                            code_task_dtos.append(
                                ProblematicCodeTaskAnalyticsDTO(
                                    code_task_id=code_task.id,
                                    section_id=section.id,
                                    title=code_task.title,
                                    students_count=len(grouped),
                                    submissions_count=len(submissions),
                                    passed_students_count=passed_students_count,
                                    pass_rate=passed_students_count / len(grouped),
                                    repeat_students_count=repeat_students_count,
                                )
                            )

            students_started_count = len(progresses)
            students_completed_count = sum(
                1
                for progress in progresses
                if progress.is_course_completed(total_sections_count)
            )
            completion_rate = (
                0.0 if not progresses else students_completed_count / len(progresses)
            )
            average_completion_ratio = (
                0.0
                if not progresses
                else sum(
                    progress.course_completion_ratio(total_sections_count)
                    for progress in progresses
                )
                / len(progresses)
            )
            average_points = (
                0.0
                if not progresses
                else sum(progress.total_points for progress in progresses)
                / len(progresses)
            )

            question_dtos.sort(key=lambda item: item.first_try_success_rate)
            task_dtos.sort(key=lambda item: item.first_try_success_rate)
            code_task_dtos.sort(key=lambda item: item.pass_rate)

            return AuthorCourseAnalyticsDTO(
                course_id=course.id,
                course_title=course.title,
                students_started_count=students_started_count,
                students_completed_count=students_completed_count,
                completion_rate=completion_rate,
                average_completion_ratio=average_completion_ratio,
                average_points=average_points,
                modules=module_dtos,
                difficult_questions=question_dtos,
                difficult_tasks=task_dtos,
                problematic_code_tasks=code_task_dtos,
            )

    @staticmethod
    def _group_question_attempts(
        attempts: list[QuestionAttempt],
    ) -> dict[UUID, list[QuestionAttempt]]:
        grouped: dict[UUID, list[QuestionAttempt]] = {}
        for attempt in attempts:
            grouped.setdefault(attempt.student_id, []).append(attempt)
        return grouped

    @staticmethod
    def _group_task_attempts(
        attempts: list[TaskAttempt],
    ) -> dict[UUID, list[TaskAttempt]]:
        grouped: dict[UUID, list[TaskAttempt]] = {}
        for attempt in attempts:
            grouped.setdefault(attempt.student_id, []).append(attempt)
        return grouped

    @staticmethod
    def _group_code_submissions(
        submissions: list[CodeSubmission],
    ) -> dict[UUID, list[CodeSubmission]]:
        grouped: dict[UUID, list[CodeSubmission]] = {}
        for submission in submissions:
            grouped.setdefault(submission.student_id, []).append(submission)
        return grouped
