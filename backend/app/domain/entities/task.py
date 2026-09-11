from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions import (
    InvalidTaskError,
    TaskAlreadySolvedError,
    TaskAttemptLimitExceededError,
)


@dataclass(slots=True)
class Task:
    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    max_attempts: int = 1
    reward_points: int = 1

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidTaskError('Task title cannot be empty.')
        if not self.statement or not self.statement.strip():
            raise InvalidTaskError('Task statement cannot be empty.')
        if self.position < 1:
            raise InvalidTaskError('Task position must be positive.')
        if self.max_attempts < 1:
            raise InvalidTaskError('Task max_attempts must be positive.')
        if self.reward_points < 1:
            raise InvalidTaskError('Task reward_points must be positive.')

    def update(self, title: str, statement: str, position: int) -> None:
        self.title = title
        self.statement = statement
        self.position = position
        self._validate()

    def allows_multiple_attempts(self) -> bool:
        return self.max_attempts > 1

    def is_single_attempt(self) -> bool:
        return self.max_attempts == 1

    def requires_submission(self) -> bool:
        return True

    def can_start_attempt(
        self,
        existing_attempts_count: int,
        has_correct_attempt: bool = False,
    ) -> bool:
        if has_correct_attempt:
            return False
        return existing_attempts_count < self.max_attempts

    def ensure_attempt_available(
        self,
        existing_attempts_count: int,
        has_correct_attempt: bool = False,
    ) -> None:
        if has_correct_attempt:
            raise TaskAlreadySolvedError('Task has already been solved successfully.')
        if not self.can_start_attempt(existing_attempts_count):
            raise TaskAttemptLimitExceededError('Task attempt limit has been reached.')