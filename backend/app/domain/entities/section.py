from dataclasses import dataclass, field
from uuid import UUID

from app.domain.exceptions import (
    InvalidSectionError,
    SectionQuestionAlreadyAttachedError,
    SectionQuestionNotAttachedError,
)


@dataclass(slots=True)
class Section:
    id: UUID
    module_id: UUID
    title: str
    description: str = ''
    position: int = 1
    lecture_ids: list[UUID] = field(default_factory=list)
    question_ids: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidSectionError('Section title cannot be empty.')
        if self.position < 1:
            raise InvalidSectionError('Section position must be positive.')

    def update(self, title: str, description: str, position: int) -> None:
        self.title = title
        self.description = description
        self.position = position
        self._validate()

    def add_lecture(self, lecture_id: UUID) -> None:
        if lecture_id not in self.lecture_ids:
            self.lecture_ids.append(lecture_id)

    def remove_lecture(self, lecture_id: UUID) -> None:
        if lecture_id in self.lecture_ids:
            self.lecture_ids.remove(lecture_id)

    def add_question(self, question_id: UUID) -> None:
        if question_id in self.question_ids:
            raise SectionQuestionAlreadyAttachedError(
                'Section already has this question attached.'
            )
        self.question_ids.append(question_id)

    def remove_question(self, question_id: UUID) -> None:
        if question_id not in self.question_ids:
            raise SectionQuestionNotAttachedError(
                'Section does not have this question attached.'
            )
        self.question_ids.remove(question_id)

    def has_questions(self) -> bool:
        return bool(self.question_ids)

    def contains_question(self, question_id: UUID) -> bool:
        return question_id in self.question_ids

    def can_be_completed(self) -> bool:
        return bool(self.question_ids)

    def is_completed_by(self, completed_question_ids: Collection[UUID]) -> bool:
        if not self.can_be_completed():
            return False
        return all(question_id in completed_question_ids for question_id in self.question_ids)