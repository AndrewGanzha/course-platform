from uuid import UUID

from app.application.exceptions import (
    CourseNotFoundError,
    ModuleNotFoundError,
    SectionNotFoundError,
)
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.domain.entities.course import Course


class LectureCourseResolver:
    """Resolves the course that owns a lecture through the content tree."""

    def __init__(
        self,
        course_repository: CourseRepository,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
    ) -> None:
        self.course_repository = course_repository
        self.module_repository = module_repository
        self.section_repository = section_repository

    async def resolve_course_for_section(self, section_id: UUID) -> Course:
        section = await self.section_repository.get_by_id(section_id)
        if section is None:
            raise SectionNotFoundError("Section not found.")

        module = await self.module_repository.get_by_id(section.module_id)
        if module is None:
            raise ModuleNotFoundError("Module not found.")

        course = await self.course_repository.get_by_id(module.course_id)
        if course is None:
            raise CourseNotFoundError("Course not found.")

        return course
