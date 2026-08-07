from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from app.domain.exceptions import (
    InvalidQuestionAttemptError,
    QuestionAttemptLimitExceededError,
)


@dataclass(slots=True)
class QuestionAttempt:
    id: UUID
    question_id: UUID
    student_id: UUID
    attempt_number: int
    selected_option_ids: list[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.attempt_number < 1:
            raise InvalidQuestionAttemptError('Question attempt number must be positive.')
        if not self.selected_option_ids:
            raise InvalidQuestionAttemptError(
                'Question attempt must contain at least one selected option.'
            )
        if len(self.selected_option_ids) != len(set(self.selected_option_ids)):
            raise InvalidQuestionAttemptError(
                'Question attempt cannot contain duplicate selected options.'
            )

    def is_first_attempt(self) -> bool:
        return self.attempt_number == 1

    def is_repeat_attempt(self) -> bool:
        return self.attempt_number > 1

    def has_selected_options(self) -> bool:
        return bool(self.selected_option_ids)

    def selected_options_count(self) -> int:
        return len(self.selected_option_ids)

    def uses_option(self, answer_option_id: UUID) -> bool:
        return answer_option_id in self.selected_option_ids

    def can_start_attempt(self, existing_attempts_count: int) -> bool:
        return existing_attempts_count < self.max_attempts

    def ensure_attempt_available(self, existing_attempts_count: int) -> None:
        if not self.can_start_attempt(existing_attempts_count):
            raise QuestionAttemptLimitExceededError('Question attempt limit has been reached.')