from dataclasses import dataclass
from uuid import UUID

from app.application.dto.student_course_analytics import (
    StudentCourseAnalyticsDTO,
    StudentModuleAnalyticsDTO,
    StudentWeakCodeTaskDTO,
    StudentWeakQuestionDTO,
    StudentWeakTaskDTO,
)
from app.application.exceptions import CourseNotFoundError, PermissionDeniedError
from app.application.interfaces.student_analytics_cache import (
    StudentAnalyticsCache,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User


@dataclass(slots=True)
class GetMyCourseAnalyticsQuery:
    actor: User
    course_id: UUID


class GetMyCourseAnalyticsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        analytics_cache: StudentAnalyticsCache | None = None,
    ) -> None:
        self.uow = uow
        self.analytics_cache = analytics_cache

    async def execute(
        self, query: GetMyCourseAnalyticsQuery
    ) -> StudentCourseAnalyticsDTO:
        if not query.actor.can_view_own_learning_results():
            raise PermissionDeniedError("User cannot view own learning analytics.")

        if self.analytics_cache is not None:
            cached = await self.analytics_cache.get(
                student_id=query.actor.id,
                course_id=query.course_id,
            )
            if cached is not None:
                return cached

        result = await self._build_analytics(query)

        if self.analytics_cache is not None:
            await self.analytics_cache.set(
                student_id=query.actor.id,
                course_id=query.course_id,
                value=result,
            )

        return result

    async def _build_analytics(
        self, query: GetMyCourseAnalyticsQuery
    ) -> StudentCourseAnalyticsDTO:
        async with self.uow:
            course = await self.uow.courses.get_by_id(query.course_id)
            if course is None:
                raise CourseNotFoundError("Course not found.")

            progress = await self.uow.progress.get_by_student_and_course(
                student_id=query.actor.id,
                course_id=course.id,
            )
            modules = await self.uow.modules.get_by_ids(course.module_ids)
            total_modules_count = len(modules)
            total_sections_count = 0
            module_dtos: list[StudentModuleAnalyticsDTO] = []
            weak_question_dtos: list[StudentWeakQuestionDTO] = []
            weak_task_dtos: list[StudentWeakTaskDTO] = []
            weak_code_task_dtos: list[StudentWeakCodeTaskDTO] = []
            completed_module_ids = set(
                progress.completed_module_ids if progress else []
            )
            completed_section_ids = set(
                progress.completed_section_ids if progress else []
            )

            for module in sorted(modules, key=lambda item: item.position):
                sections = await self.uow.sections.get_by_ids(module.section_ids)
                total_sections_count += len(sections)
                completed_sections_in_module = 0

                for section in sections:
                    if section.id in completed_section_ids:
                        completed_sections_in_module += 1

                    for question_id in section.question_ids:
                        attempts = await self.uow.question_attempts.get_by_student_and_question(
                            query.actor.id,
                            question_id,
                        )
                        if len(attempts) > 1:
                            weak_question_dtos.append(
                                StudentWeakQuestionDTO(
                                    question_id=question_id,
                                    section_id=section.id,
                                    attempts_count=len(attempts),
                                )
                            )

                    for task_id in section.task_ids:
                        attempts = await self.uow.task_attempts.get_by_student_and_task(
                            query.actor.id,
                            task_id,
                        )
                        if len(attempts) > 1:
                            weak_task_dtos.append(
                                StudentWeakTaskDTO(
                                    task_id=task_id,
                                    section_id=section.id,
                                    attempts_count=len(attempts),
                                )
                            )

                    for code_task_id in section.code_task_ids:
                        submissions = await self.uow.code_submissions.get_by_student_and_code_task(
                            student_id=query.actor.id,
                            code_task_id=code_task_id,
                        )
                        if self._is_weak_code_task(submissions):
                            weak_code_task_dtos.append(
                                StudentWeakCodeTaskDTO(
                                    code_task_id=code_task_id,
                                    section_id=section.id,
                                    attempts_count=len(submissions),
                                )
                            )

                module_dtos.append(
                    StudentModuleAnalyticsDTO(
                        module_id=module.id,
                        title=module.title,
                        completed_sections_count=completed_sections_in_module,
                        total_sections_count=len(sections),
                        is_completed=module.id in completed_module_ids,
                    )
                )

            completion_ratio = (
                0.0
                if progress is None
                else progress.course_completion_ratio(total_sections_count)
            )
            is_completed = (
                False
                if progress is None
                else progress.is_course_completed(total_sections_count)
            )
            total_points = 0 if progress is None else progress.total_points
            completed_modules_count = (
                0 if progress is None else progress.completed_modules_count()
            )
            completed_sections_count = (
                0 if progress is None else progress.completed_sections_count()
            )

            return StudentCourseAnalyticsDTO(
                course_id=course.id,
                course_title=course.title,
                completion_ratio=completion_ratio,
                is_completed=is_completed,
                total_points=total_points,
                completed_modules_count=completed_modules_count,
                total_modules_count=total_modules_count,
                completed_sections_count=completed_sections_count,
                total_sections_count=total_sections_count,
                modules=module_dtos,
                weak_questions=weak_question_dtos,
                weak_tasks=weak_task_dtos,
                weak_code_tasks=weak_code_task_dtos,
            )

    @staticmethod
    def _is_weak_code_task(submissions: list) -> bool:
        if len(submissions) > 1:
            return True
        return any(submission.status.value == "failed" for submission in submissions)
