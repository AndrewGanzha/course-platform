from dataclasses import dataclass

from app.application.dto.user_profile import UserProfileDTO
from app.domain.entities.user import User


@dataclass(slots=True)
class GetMyProfileQuery:
    actor: User


class GetMyProfileUseCase:
    async def execute(self, query: GetMyProfileQuery) -> UserProfileDTO:
        return UserProfileDTO(
            id=query.actor.id,
            email=query.actor.email,
            role=query.actor.role,
            full_name=query.actor.full_name,
            bio=query.actor.bio,
            avatar_url=query.actor.avatar_url,
        )
