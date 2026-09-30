from app.application.dto.course_catalog import (
    CourseCatalogCardDTO,
    CourseCatalogCountersDTO,
    CourseCatalogItemDTO,
    CourseCatalogModulePreviewDTO,
    CourseCatalogSectionPreviewDTO,
)
from app.application.interfaces.repositories.code_task_repository import (
    CodeTaskRepository,
)
from app.application.interfaces.repositories.lecture_repository import LectureRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.question_repository import (
    QuestionRepository,
)
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.application.interfaces.repositories.task_repository import TaskRepository
from app.domain.entities.course import Course


class CourseCatalogReadService:
    def __init__(
        self,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
        lecture_repository: LectureRepository,
        question_repository: QuestionRepository,
        task_repository: TaskRepository,
        code_task_repository: CodeTaskRepository,
    ) -> None:
        self.module_repository = module_repository
        self.section_repository = section_repository
        self.lecture_repository = lecture_repository
        self.question_repository = question_repository
        self.task_repository = task_repository
        self.code_task_repository = code_task_repository

    async def build_catalog_item(self, course: Course) -> CourseCatalogItemDTO:
        counters = await self._build_counters(course)
        return CourseCatalogItemDTO(
            id=course.id,
            title=course.title,
            short_description=course.preview_description(),
            cover_image_url=course.cover_image_url,
            difficulty=course.difficulty,
            tag_names=list(course.tag_names),
            status=course.status,
            counters=counters,
        )

    async def build_course_card(self, course: Course) -> CourseCatalogCardDTO:
        counters = await self._build_counters(course)
        modules = await self.module_repository.get_by_ids(course.module_ids)
        module_dtos: list[CourseCatalogModulePreviewDTO] = []

        for module in sorted(modules, key=lambda item: item.position):
            sections = await self.section_repository.get_by_ids(module.section_ids)
            section_dtos = [
                CourseCatalogSectionPreviewDTO(
                    id=section.id,
                    title=section.title,
                    position=section.position,
                )
                for section in sorted(sections, key=lambda item: item.position)
            ]
            module_dtos.append(
                CourseCatalogModulePreviewDTO(
                    id=module.id,
                    title=module.title,
                    description=module.description,
                    position=module.position,
                    sections=section_dtos,
                )
            )

        return CourseCatalogCardDTO(
            id=course.id,
            title=course.title,
            description=course.description,
            short_description=course.preview_description(),
            cover_image_url=course.cover_image_url,
            difficulty=course.difficulty,
            tag_names=list(course.tag_names),
            status=course.status,
            counters=counters,
            modules=module_dtos,
        )

    async def _build_counters(self, course: Course) -> CourseCatalogCountersDTO:
        modules = await self.module_repository.get_by_ids(course.module_ids)

        section_count = 0
        lecture_count = 0
        question_count = 0
        task_count = 0
        code_task_count = 0

        for module in modules:
            sections = await self.section_repository.get_by_ids(module.section_ids)
            section_count += len(sections)

            for section in sections:
                lectures = await self.lecture_repository.get_by_ids(section.lecture_ids)
                questions = await self.question_repository.get_by_ids(
                    section.question_ids
                )
                tasks = await self.task_repository.get_by_ids(section.task_ids)
                code_tasks = await self.code_task_repository.get_by_ids(
                    section.code_task_ids
                )

                lecture_count += len(lectures)
                question_count += len(questions)
                task_count += len(tasks)
                code_task_count += len(code_tasks)

        return CourseCatalogCountersDTO(
            module_count=len(modules),
            section_count=section_count,
            lecture_count=lecture_count,
            question_count=question_count,
            task_count=task_count,
            code_task_count=code_task_count,
        )
