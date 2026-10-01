from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.user import UserRole


@dataclass(slots=True)
class UserProfileDTO:
    id: UUID
    email: str
    role: UserRole
    full_name: str
    bio: str
    avatar_url: str | None
