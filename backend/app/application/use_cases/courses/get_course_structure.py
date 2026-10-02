from dataclasses import dataclass
from uuid import UUID

from app.application.dto.course_structure import (
    CodeTaskStructureDTO,
    CourseStructureDTO,
    LectureStructureDTO,
    ModuleStructureDTO,
    SectionStructureDTO,
    TaskStructureDTO,
)
from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.repositories.code_task_repository import (
    CodeTaskRepository,
)
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.interfaces.repositories.lecture_repository import LectureRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.application.interfaces.repositories.task_repository import TaskRepository
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class GetCourseStructureQuery:
    course_id: UUID
    actor: User | None = None


class GetCourseStructureUseCase:
    def __init__(
        self,
        course_repository: CourseRepository,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
        lecture_repository: LectureRepository,
        task_repository: TaskRepository,
        code_task_repository: CodeTaskRepository,
        access_service: CourseContentAccessService,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.course_repository = course_repository
        self.module_repository = module_repository
        self.section_repository = section_repository
        self.lecture_repository = lecture_repository
        self.task_repository = task_repository
        self.code_task_repository = code_task_repository
        self.access_service = access_service
        self.content_cache = content_cache

    async def execute(self, query: GetCourseStructureQuery) -> CourseStructureDTO:
        course = await self.course_repository.get_by_id(query.course_id)
        if course is None:
            raise CourseNotFoundError("Course not found.")

        can_view = await self.access_service.can_view_course(
            course_id=course.id,
            actor=query.actor,
        )
        if not can_view:
            raise CourseNotFoundError("Course not found.")

        can_use_public_cache = (
            query.actor is None
            and course.is_publicly_visible()
            and self.content_cache is not None
        )

        if can_use_public_cache:
            cached = await self.content_cache.get_course_structure(course.id)
            if cached is not None:
                return cached

        modules = await self.module_repository.get_by_ids(course.module_ids)
        module_dtos: list[ModuleStructureDTO] = []

        for module in sorted(modules, key=lambda item: item.position):
            sections = await self.section_repository.get_by_ids(module.section_ids)
            section_dtos: list[SectionStructureDTO] = []

            for section in sorted(sections, key=lambda item: item.position):
                lectures = await self.lecture_repository.get_by_ids(section.lecture_ids)
                tasks = await self.task_repository.get_by_ids(section.task_ids)
                code_tasks = await self.code_task_repository.get_by_ids(
                    section.code_task_ids
                )

                task_dtos = [
                    TaskStructureDTO(
                        id=task.id,
                        title=task.title,
                        position=task.position,
                    )
                    for task in sorted(tasks, key=lambda item: item.position)
                ]

                code_task_dtos = [
                    CodeTaskStructureDTO(
                        id=code_task.id,
                        title=code_task.title,
                        position=code_task.position,
                        language=str(code_task.language),
                    )
                    for code_task in sorted(code_tasks, key=lambda item: item.position)
                ]

                lecture_dtos = [
                    LectureStructureDTO(
                        id=lecture.id,
                        title=lecture.title,
                        position=lecture.position,
                    )
                    for lecture in sorted(lectures, key=lambda item: item.position)
                ]

                section_dtos.append(
                    SectionStructureDTO(
                        id=section.id,
                        title=section.title,
                        description=section.description,
                        position=section.position,
                        question_ids=list(section.question_ids),
                        task_ids=list(section.task_ids),
                        code_task_ids=list(section.code_task_ids),
                        tasks=task_dtos,
                        code_tasks=code_task_dtos,
                        lectures=lecture_dtos,
                    )
                )

            module_dtos.append(
                ModuleStructureDTO(
                    id=module.id,
                    title=module.title,
                    description=module.description,
                    position=module.position,
                    sections=section_dtos,
                )
            )

        result = CourseStructureDTO(
            id=course.id,
            title=course.title,
            description=course.description,
            status=course.status,
            short_description=course.short_description,
            cover_image_url=course.cover_image_url,
            difficulty=course.difficulty,
            tag_names=list(course.tag_names),
            modules=module_dtos,
        )

        if can_use_public_cache:
            await self.content_cache.set_course_structure(course.id, result)

        return result
