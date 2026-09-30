from dataclasses import dataclass, field

from app.application.dto.course_catalog import CourseCatalogItemDTO
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.services.course_catalog_read_service import (
    CourseCatalogReadService,
)
from app.domain.entities.course import CourseDifficulty


@dataclass(slots=True)
class GetCoursesQuery:
    search: str = ""
    difficulty: CourseDifficulty | None = None
    tag_names: list[str] = field(default_factory=list)


class GetCoursesUseCase:
    def __init__(
        self,
        course_repository: CourseRepository,
        catalog_read_service: CourseCatalogReadService,
    ) -> None:
        self.course_repository = course_repository
        self.catalog_read_service = catalog_read_service

    def _normalize_tags(self, tag_names: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for raw_tag in tag_names:
            tag = raw_tag.strip().lower()
            if not tag:
                continue
            if tag not in seen:
                seen.add(tag)
                normalized.append(tag)

        return normalized

    async def execute(self, query: GetCoursesQuery) -> list[CourseCatalogItemDTO]:
        search = query.search.strip()
        tag_names = self._normalize_tags(query.tag_names)

        courses = await self.course_repository.find_published_catalog_courses(
            search=search,
            difficulty=query.difficulty,
        )

        if tag_names:
            courses = [
                course
                for course in courses
                if all(tag in course.tag_names for tag in tag_names)
            ]

        items: list[CourseCatalogItemDTO] = []
        for course in courses:
            items.append(await self.catalog_read_service.build_catalog_item(course))

        return items
