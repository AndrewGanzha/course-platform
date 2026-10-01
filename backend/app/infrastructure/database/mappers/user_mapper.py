from uuid import UUID

from app.domain.entities.user import User, UserRole
from app.infrastructure.database.models.user_model import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=UUID(model.id),
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            full_name=model.full_name,
            bio=model.bio,
            avatar_url=model.avatar_url,
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=str(user.id),
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
        )
