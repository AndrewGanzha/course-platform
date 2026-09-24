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
from app.application.interfaces.repositories.code_task_repository import (
    CodeTaskRepository,
)
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.interfaces.repositories.lecture_repository import LectureRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.application.interfaces.repositories.task_repository import TaskRepository


@dataclass(slots=True)
class GetCourseStructureQuery:
    course_id: UUID


class GetCourseStructureUseCase:
    def __init__(
        self,
        course_repository: CourseRepository,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
        lecture_repository: LectureRepository,
        task_repository: TaskRepository,
        code_task_repository: CodeTaskRepository,
    ) -> None:
        self.course_repository = course_repository
        self.module_repository = module_repository
        self.section_repository = section_repository
        self.lecture_repository = lecture_repository
        self.task_repository = task_repository
        self.code_task_repository = code_task_repository

    async def execute(self, query: GetCourseStructureQuery) -> CourseStructureDTO:
        course = await self.course_repository.get_by_id(query.course_id)
        if course is None:
            raise CourseNotFoundError("Course not found.")

        modules = await self.module_repository.get_by_ids(course.module_ids)
        module_dtos: list[ModuleStructureDTO] = []

        for module in sorted(modules, key=lambda item: item.position):
            sections = await self.section_repository.get_by_ids(module.section_ids)
            section_dtos: list[SectionStructureDTO] = []

            for section in sorted(sections, key=lambda item: item.position):
                lectures = await self.lecture_repository.get_by_ids(section.lecture_ids)
                lecture_dtos = [
                    LectureStructureDTO(
                        id=lecture.id,
                        title=lecture.title,
                        position=lecture.position,
                    )
                    for lecture in sorted(lectures, key=lambda item: item.position)
                ]

                tasks = await self.task_repository.get_by_ids(section.task_ids)
                task_dtos = [
                    TaskStructureDTO(
                        id=task.id,
                        title=task.title,
                        position=task.position,
                    )
                    for task in sorted(tasks, key=lambda item: item.position)
                ]

                code_tasks = await self.code_task_repository.get_by_ids(
                    section.code_task_ids
                )
                code_task_dtos = [
                    CodeTaskStructureDTO(
                        id=code_task.id,
                        title=code_task.title,
                        position=code_task.position,
                        language=str(code_task.language),
                    )
                    for code_task in sorted(code_tasks, key=lambda item: item.position)
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

        return CourseStructureDTO(
            id=course.id,
            title=course.title,
            description=course.description,
            modules=module_dtos,
        )
