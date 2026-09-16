from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidCodeTaskError


class CodeTaskLanguage(StrEnum):
    PYTHON = 'python'


@dataclass(slots=True)
class CodeTask:
    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    language: CodeTaskLanguage = CodeTaskLanguage.PYTHON
    starter_code: str = ''
    max_attempts: int = 1
    reward_points: int = 1
    time_limit_seconds: int = 2
    memory_limit_mb: int = 128

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidCodeTaskError('CodeTask title cannot be empty.')
        if not self.statement or not self.statement.strip():
            raise InvalidCodeTaskError('CodeTask statement cannot be empty.')
        if self.position < 1:
            raise InvalidCodeTaskError('CodeTask position must be positive.')
        if self.max_attempts < 1:
            raise InvalidCodeTaskError('CodeTask max_attempts must be positive.')
        if self.reward_points < 1:
            raise InvalidCodeTaskError('CodeTask reward_points must be positive.')
        if self.time_limit_seconds < 1:
            raise InvalidCodeTaskError('CodeTask time_limit_seconds must be positive.')
        if self.memory_limit_mb < 16:
            raise InvalidCodeTaskError('CodeTask memory_limit_mb is too small.')

    def update(
            self,
            title: str,
            statement: str,
            position: int,
            starter_code: str,
    ) -> None:
        self.title = title
        self.statement = statement
        self.position = position
        self.starter_code = starter_code
        self._validate()

    def allows_multiple_attempts(self) -> bool:
        return self.max_attempts > 1

    def is_single_attempt(self) -> bool:
        return self.max_attempts == 1

    def requires_submission(self) -> bool:
        return True

    def requires_external_check(self) -> bool:
        return True

    def supports_inline_answer_check(self) -> bool:
        return False

    def requires_test_case_execution(self) -> bool:
        return True
