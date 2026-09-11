from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions import InvalidTaskError


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