from app.application.dto.course_catalog import (
    CourseCatalogCardDTO,
    CourseCatalogItemDTO,
    CourseCatalogModulePreviewDTO,
    CourseCatalogSectionPreviewDTO,
)
from app.application.interfaces.repositories.course_catalog_metrics_repository import (
    CourseCatalogMetricsRepository,
)
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.domain.entities.course import Course


class CourseCatalogReadService:
    def __init__(
        self,
        metrics_repository: CourseCatalogMetricsRepository,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
    ) -> None:
        self.metrics_repository = metrics_repository
        self.module_repository = module_repository
        self.section_repository = section_repository

    async def build_catalog_items(
        self,
        courses: list[Course],
    ) -> list[CourseCatalogItemDTO]:
        metrics_by_course = await self.metrics_repository.get_by_course_ids(
            [course.id for course in courses]
        )

        return [
            CourseCatalogItemDTO(
                id=course.id,
                title=course.title,
                short_description=course.preview_description(),
                cover_image_url=course.cover_image_url,
                difficulty=course.difficulty,
                tag_names=list(course.tag_names),
                status=course.status,
                counters=metrics_by_course[course.id].counters,
                rating=metrics_by_course[course.id].rating,
            )
            for course in courses
        ]

    async def build_course_card(self, course: Course) -> CourseCatalogCardDTO:
        metrics_by_course = await self.metrics_repository.get_by_course_ids([course.id])
        metrics = metrics_by_course[course.id]

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
            counters=metrics.counters,
            rating=metrics.rating,
            modules=module_dtos,
        )
