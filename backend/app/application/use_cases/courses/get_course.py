from dataclasses import dataclass
from uuid import UUID

from app.application.dto.course_catalog import CourseCatalogCardDTO
from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.services.course_catalog_read_service import (
    CourseCatalogReadService,
)
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class GetCourseQuery:
    course_id: UUID
    actor: User | None = None


class GetCourseUseCase:
    def __init__(
        self,
        course_repository: CourseRepository,
        access_service: CourseContentAccessService,
        catalog_read_service: CourseCatalogReadService,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.course_repository = course_repository
        self.access_service = access_service
        self.catalog_read_service = catalog_read_service
        self.content_cache = content_cache

    async def execute(self, query: GetCourseQuery) -> CourseCatalogCardDTO:
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
            cached = await self.content_cache.get_course_card(course.id)
            if cached is not None:
                return cached

        result = await self.catalog_read_service.build_course_card(course)

        if can_use_public_cache:
            await self.content_cache.set_course_card(course.id, result)

        return result
