from dataclasses import dataclass, field
from uuid import UUID

from app.domain.entities.course import CourseStatus


@dataclass(slots=True)
class CourseCatalogCountersDTO:
    module_count: int
    section_count: int
    lecture_count: int
    question_count: int
    task_count: int
    code_task_count: int


@dataclass(slots=True)
class CourseCatalogItemDTO:
    id: UUID
    title: str
    description: str
    status: CourseStatus
    counters: CourseCatalogCountersDTO


@dataclass(slots=True)
class CourseCatalogSectionPreviewDTO:
    id: UUID
    title: str
    position: int


@dataclass(slots=True)
class CourseCatalogModulePreviewDTO:
    id: UUID
    title: str
    description: str
    position: int
    sections: list[CourseCatalogSectionPreviewDTO] = field(default_factory=list)


@dataclass(slots=True)
class CourseCatalogCardDTO:
    id: UUID
    title: str
    description: str
    status: CourseStatus
    counters: CourseCatalogCountersDTO
    modules: list[CourseCatalogModulePreviewDTO] = field(default_factory=list)
