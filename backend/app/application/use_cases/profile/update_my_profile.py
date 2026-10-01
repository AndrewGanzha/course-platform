from dataclasses import dataclass

from app.application.dto.user_profile import UserProfileDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateMyProfileCommand:
    actor: User
    full_name: str
    bio: str
    avatar_url: str | None


class UpdateMyProfileUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpdateMyProfileCommand) -> UserProfileDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(command.actor.id)
            if user is None:
                raise RuntimeError("Authenticated user was not found.")

            user.update_profile(
                full_name=command.full_name,
                bio=command.bio,
                avatar_url=command.avatar_url,
            )
            await self.uow.users.update(user)
            await self.uow.commit()

            return UserProfileDTO(
                id=user.id,
                email=user.email,
                role=user.role,
                full_name=user.full_name,
                bio=user.bio,
                avatar_url=user.avatar_url,
            )
