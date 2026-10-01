from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.domain.entities.user import UserRole


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: UserRole
    full_name: str
    bio: str
    avatar_url: str | None


class UpdateMyProfileRequest(BaseModel):
    full_name: str = Field(default="", max_length=120)
    bio: str = Field(default="", max_length=500)
    avatar_url: HttpUrl | None = None
