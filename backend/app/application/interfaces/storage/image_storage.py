from abc import ABC, abstractmethod
from uuid import UUID


class ImageStorage(ABC):
    @abstractmethod
    async def save(
        self,
        *,
        course_id: UUID,
        filename: str,
        content: bytes,
    ) -> str:
        """Persist an image and return the public URL that points to it."""
        raise NotImplementedError
