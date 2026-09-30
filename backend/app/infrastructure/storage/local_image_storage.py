import asyncio
from pathlib import Path
from uuid import UUID, uuid4

from app.application.interfaces.storage.image_storage import ImageStorage


class LocalImageStorage(ImageStorage):
    def __init__(
        self,
        root: Path,
        url_prefix: str,
        subdirectory: str = "course-covers",
    ) -> None:
        self.root = root
        self.url_prefix = url_prefix.rstrip("/")
        self.subdirectory = subdirectory

    async def save(
        self,
        *,
        course_id: UUID,
        filename: str,
        content: bytes,
    ) -> str:
        extension = Path(filename).suffix.lower()
        relative_directory = Path(self.subdirectory) / str(course_id)
        target_directory = self.root / relative_directory
        target_directory.mkdir(parents=True, exist_ok=True)

        object_name = f"{uuid4().hex}{extension}"
        target_path = target_directory / object_name
        await asyncio.to_thread(target_path.write_bytes, content)

        relative_path = (relative_directory / object_name).as_posix()
        return f"{self.url_prefix}/{relative_path}"
