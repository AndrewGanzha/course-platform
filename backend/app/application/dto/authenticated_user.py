from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.user import UserRole


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    id: UUID
    email: str
    role: UserRole
