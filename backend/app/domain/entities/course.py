from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import (  # New
    InvalidCourseError,
    InvalidCourseStatusTransitionError,
)


class CourseStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass(slots=True)
class Course:
    id: UUID
    author_id: UUID
    title: str
    description: str
    status: CourseStatus = CourseStatus.DRAFT
    module_ids: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidCourseError("Course title cannot be empty.")
        if not self.description or not self.description.strip():
            raise InvalidCourseError("Course description cannot be empty.")

    def update(self, title: str, description: str) -> None:
        self.title = title
        self.description = description
        self._validate()

    def is_owned_by(self, user_id: UUID) -> bool:
        return self.author_id == user_id

    def is_draft(self) -> bool:
        return self.status == CourseStatus.DRAFT

    def is_published(self) -> bool:
        return self.status == CourseStatus.PUBLISHED

    def is_archived(self) -> bool:
        return self.status == CourseStatus.ARCHIVED

    def is_publicly_visible(self) -> bool:
        return self.is_published()

    def publish(self) -> None:
        if self.is_published():
            raise InvalidCourseStatusTransitionError("Course is already published.")
        self.status = CourseStatus.PUBLISHED

    def archive(self) -> None:  # New
        if not self.is_published():
            raise InvalidCourseStatusTransitionError(
                "Only published courses can be archived."
            )
        self.status = CourseStatus.ARCHIVED

    def add_module(self, module_id: UUID) -> None:
        if module_id not in self.module_ids:
            self.module_ids.append(module_id)

    def remove_module(self, module_id: UUID) -> None:
        if module_id in self.module_ids:
            self.module_ids.remove(module_id)
