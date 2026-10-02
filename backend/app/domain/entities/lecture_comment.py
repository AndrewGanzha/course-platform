from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.domain.exceptions import InvalidLectureCommentError

MAX_COMMENT_LENGTH = 2000


@dataclass(slots=True)
class LectureComment:
    id: UUID
    lecture_id: UUID
    user_id: UUID
    text: str
    created_at: datetime
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self.text = self.text.strip()
        self._validate()

    def _validate(self) -> None:
        if not self.text:
            raise InvalidLectureCommentError("Lecture comment text cannot be empty.")
        if len(self.text) > MAX_COMMENT_LENGTH:
            raise InvalidLectureCommentError(
                f"Lecture comment text cannot be longer than {MAX_COMMENT_LENGTH} "
                "characters."
            )

    def update(self, *, text: str) -> None:
        self.text = text.strip()
        self._validate()
        self.updated_at = datetime.now(UTC)

    def is_written_by(self, user_id: UUID) -> bool:
        return self.user_id == user_id
