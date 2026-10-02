from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dto.course_catalog import CourseCatalogMetricsDTO


class CourseCatalogMetricsRepository(ABC):
    @abstractmethod
    async def get_by_course_ids(
        self,
        course_ids: list[UUID],
    ) -> dict[UUID, CourseCatalogMetricsDTO]:
        raise NotImplementedError
