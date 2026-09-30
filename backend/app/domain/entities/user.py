from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidUserError


class UserRole(StrEnum):
    STUDENT = "student"
    AUTHOR = "author"
    ADMIN = "admin"


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    hashed_password: str
    role: UserRole
    full_name: str = ""
    bio: str = ""
    avatar_url: str | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.email or "@" not in self.email:
            raise InvalidUserError("User email is invalid.")
        if not self.hashed_password or not self.hashed_password.strip():
            raise InvalidUserError("User hashed password cannot be empty.")
        if len(self.full_name) > 120:
            raise InvalidUserError(
                "User full name cannot be longer than 120 characters."
            )
        if len(self.bio) > 500:
            raise InvalidUserError("User bio cannot be longer than 500 characters.")
        if self.avatar_url is not None and not self.avatar_url.strip():
            raise InvalidUserError("User avatar URL cannot be empty when provided.")

    def update_profile(
        self,
        *,
        full_name: str,
        bio: str,
        avatar_url: str | None,
    ) -> None:
        self.full_name = full_name
        self.bio = bio
        self.avatar_url = avatar_url
        self._validate()

    def is_admin(self) -> bool:
        return self.role is UserRole.ADMIN

    def is_author(self) -> bool:
        return self.role is UserRole.AUTHOR

    def is_student(self) -> bool:
        return self.role is UserRole.STUDENT

    def can_manage_platform(self) -> bool:
        return self.is_admin()

    def can_manage_learning_content(self) -> bool:
        return self.role in {UserRole.ADMIN, UserRole.AUTHOR}

    def can_manage_course_structure(self) -> bool:
        return self.role in {UserRole.ADMIN, UserRole.AUTHOR}

    def can_manage_interactive_content(self) -> bool:
        return self.role in {UserRole.ADMIN, UserRole.AUTHOR}

    def can_manage_task_content(self) -> bool:
        return self.role in {UserRole.ADMIN, UserRole.AUTHOR}

    def can_take_learning_activities(self) -> bool:
        return self.is_student()

    def can_submit_task_solutions(self) -> bool:
        return self.is_student()

    def can_view_own_learning_results(self) -> bool:
        return self.is_student()

    def can_view_own_task_attempts(self) -> bool:
        return self.is_student()

    def can_view_all_learning_results(self) -> bool:
        return self.role in {UserRole.ADMIN, UserRole.AUTHOR}

    def can_manage_content(self) -> bool:
        return self.can_manage_learning_content()

    def can_view_task_attempt_results_as_author(self) -> bool:
        return self.is_author()

    def can_view_task_attempt_results_as_admin(self) -> bool:
        return self.is_admin()
