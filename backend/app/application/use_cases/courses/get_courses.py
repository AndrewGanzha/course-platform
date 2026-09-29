from dataclasses import dataclass

from app.application.dto.course_catalog import CourseCatalogItemDTO
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.services.course_catalog_read_service import (
    CourseCatalogReadService,
)


@dataclass(slots=True)
class GetCoursesQuery:
    pass


class GetCoursesUseCase:
    def __init__(
        self,
        course_repository: CourseRepository,
        catalog_read_service: CourseCatalogReadService,
    ) -> None:
        self.course_repository = course_repository
        self.catalog_read_service = catalog_read_service

    async def execute(self, query: GetCoursesQuery) -> list[CourseCatalogItemDTO]:
        courses = await self.course_repository.list_published()
        items: list[CourseCatalogItemDTO] = []

        for course in courses:
            items.append(await self.catalog_read_service.build_catalog_item(course))

        return items
