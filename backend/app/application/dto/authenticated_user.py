from typing import NewType

from app.domain.entities.user import User


AuthenticatedUser = NewType("AuthenticatedUser", User)
AuthenticatedAdmin = NewType("AuthenticatedAdmin", User)
