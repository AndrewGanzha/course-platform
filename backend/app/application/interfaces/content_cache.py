from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dto.course_catalog import (
    CourseCatalogCardDTO,
    CourseCatalogItemDTO,
)
from app.application.dto.course_structure import CourseStructureDTO


class ContentCache(ABC):
    @abstractmethod
    async def get_catalog(
        self,
        key: str,
    ) -> list[CourseCatalogItemDTO] | None:
        raise NotImplementedError

    @abstractmethod
    async def set_catalog(
        self,
        key: str,
        value: list[CourseCatalogItemDTO],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_course_card(
        self,
        course_id: UUID,
    ) -> CourseCatalogCardDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def set_course_card(
        self,
        course_id: UUID,
        value: CourseCatalogCardDTO,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_course_structure(
        self,
        course_id: UUID,
    ) -> CourseStructureDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def set_course_structure(
        self,
        course_id: UUID,
        value: CourseStructureDTO,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def invalidate_course(
        self,
        course_id: UUID,
    ) -> None:
        raise NotImplementedError
