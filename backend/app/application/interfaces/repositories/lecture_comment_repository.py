from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.lecture_comment import LectureComment


class LectureCommentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, comment_id: UUID) -> LectureComment | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_lecture_id(self, lecture_id: UUID) -> list[LectureComment]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, comment: LectureComment) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, comment: LectureComment) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, comment_id: UUID) -> None:
        raise NotImplementedError
