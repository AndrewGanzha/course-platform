from uuid import UUID

from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.domain.entities.course import Course
from app.domain.entities.user import User


class CourseContentAccessService:
    def __init__(
        self,
        course_repository: CourseRepository,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
    ) -> None:
        self.course_repository = course_repository
        self.module_repository = module_repository
        self.section_repository = section_repository

    async def can_view_course(
        self,
        course_id: UUID,
        actor: User | None,
    ) -> bool:
        course = await self.course_repository.get_by_id(course_id)
        if course is None:
            return False

        return self._can_view_course(course=course, actor=actor)

    async def can_view_section_content(
        self,
        section_id: UUID,
        actor: User | None,
    ) -> bool:
        section = await self.section_repository.get_by_id(section_id)
        if section is None:
            return False

        module = await self.module_repository.get_by_id(section.module_id)
        if module is None:
            return False

        course = await self.course_repository.get_by_id(module.course_id)
        if course is None:
            return False

        return self._can_view_course(course=course, actor=actor)

    def _can_view_course(
        self,
        course: Course,
        actor: User | None,
    ) -> bool:
        if course.is_publicly_visible():
            return True

        if actor is None:
            return False

        if actor.can_manage_platform():
            return True

        if course.is_owned_by(actor.id):
            return True

        return False
