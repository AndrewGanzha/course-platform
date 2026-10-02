from dataclasses import dataclass, field

from app.application.dto.course_catalog import CourseCatalogItemDTO
from app.application.interfaces.content_cache import ContentCache
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
        content_cache: ContentCache | None = None,
    ) -> None:
        self.course_repository = course_repository
        self.catalog_read_service = catalog_read_service
        self.content_cache = content_cache

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

    def _build_cache_key(
        self,
        *,
        search: str,
        difficulty: CourseDifficulty | None,
        tag_names: list[str],
    ) -> str:
        difficulty_value = difficulty.value if difficulty is not None else "any"
        tags_value = ",".join(sorted(tag_names)) or "any"

        return (
            f"search={search.lower()}:difficulty={difficulty_value}:tags={tags_value}"
        )

    async def execute(self, query: GetCoursesQuery) -> list[CourseCatalogItemDTO]:
        search = query.search.strip()
        tag_names = self._normalize_tags(query.tag_names)
        cache_key = self._build_cache_key(
            search=search,
            difficulty=query.difficulty,
            tag_names=tag_names,
        )

        if self.content_cache is not None:
            cached = await self.content_cache.get_catalog(cache_key)
            if cached is not None:
                return cached

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

        result = await self.catalog_read_service.build_catalog_items(courses)

        if self.content_cache is not None:
            await self.content_cache.set_catalog(cache_key, result)

        return result
