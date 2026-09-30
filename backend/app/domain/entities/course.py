from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import (
    InvalidCourseError,
    InvalidCourseStatusTransitionError,
)


class CourseStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CourseDifficulty(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass(slots=True)
class Course:
    id: UUID
    author_id: UUID
    title: str
    description: str
    status: CourseStatus = CourseStatus.DRAFT
    cover_image_url: str | None = None
    short_description: str = ""
    difficulty: CourseDifficulty = CourseDifficulty.BEGINNER
    tag_names: list[str] = field(default_factory=list)
    module_ids: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tag_names = self._normalize_tag_names(self.tag_names)
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidCourseError("Course title cannot be empty.")
        if not self.description or not self.description.strip():
            raise InvalidCourseError("Course description cannot be empty.")
        if self.cover_image_url is not None and not self.cover_image_url.strip():
            raise InvalidCourseError(
                "Course cover image URL cannot be empty when provided."
            )
        if len(self.short_description) > 280:
            raise InvalidCourseError(
                "Course short description cannot be longer than 280 characters."
            )
        if len(self.tag_names) > 10:
            raise InvalidCourseError("Course cannot have more than 10 tags.")

    def _normalize_tag_names(self, tag_names: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for raw_tag in tag_names:
            tag = raw_tag.strip().lower()
            if not tag:
                continue
            if len(tag) > 32:
                raise InvalidCourseError(
                    "Course tag cannot be longer than 32 characters."
                )
            if tag not in seen:
                seen.add(tag)
                normalized.append(tag)

        return normalized

    def update(self, title: str, description: str) -> None:
        self.title = title
        self.description = description
        self._validate()

    def update_metadata(
        self,
        *,
        cover_image_url: str | None,
        short_description: str,
        difficulty: CourseDifficulty,
        tag_names: list[str],
    ) -> None:
        self.cover_image_url = cover_image_url
        self.short_description = short_description
        self.difficulty = difficulty
        self.tag_names = self._normalize_tag_names(tag_names)
        self._validate()

    def preview_description(self) -> str:
        return self.short_description or self.description

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

    def archive(self) -> None:
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
