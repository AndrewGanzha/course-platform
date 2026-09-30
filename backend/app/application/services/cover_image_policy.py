from dataclasses import dataclass, field
from pathlib import Path

from app.application.exceptions import InvalidCoverImageError

CONTENT_TYPE_BY_EXTENSION = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


@dataclass(slots=True)
class CoverImagePolicy:
    max_size_bytes: int
    content_type_by_extension: dict[str, str] = field(
        default_factory=lambda: dict(CONTENT_TYPE_BY_EXTENSION)
    )

    def validate(
        self,
        *,
        filename: str,
        content_type: str | None,
        size: int,
    ) -> None:
        extension = Path(filename).suffix.lower()
        expected_content_type = self.content_type_by_extension.get(extension)

        if expected_content_type is None:
            raise InvalidCoverImageError(
                "Unsupported cover image extension. "
                "Allowed extensions: .jpg, .jpeg, .png, .webp, .gif."
            )

        if content_type != expected_content_type:
            raise InvalidCoverImageError(
                "Cover image content type does not match the file extension. "
                f"Expected '{expected_content_type}' for '{extension}'."
            )

        if size <= 0:
            raise InvalidCoverImageError("Cover image file is empty.")

        if size > self.max_size_bytes:
            raise InvalidCoverImageError(
                "Cover image exceeds the maximum allowed size of "
                f"{self.max_size_bytes} bytes."
            )
