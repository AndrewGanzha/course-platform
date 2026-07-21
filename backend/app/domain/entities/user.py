from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidUserError


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    hashed_password: str
    role: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.email or "@" not in self.email:
            raise InvalidUserError("User email is invalid.")
        if not self.hashed_password or not self.hashed_password.strip():
            raise InvalidUserError("User hashed password cannot be empty.")