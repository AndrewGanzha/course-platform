from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class LectureCommentDTO:
    id: UUID
    lecture_id: UUID
    user_id: UUID
    text: str
    created_at: datetime
    updated_at: datetime | None
