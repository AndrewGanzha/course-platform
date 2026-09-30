from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))
    full_name: Mapped[str] = mapped_column(String(120), server_default="")
    bio: Mapped[str] = mapped_column(String(500), server_default="")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    courses = relationship(
        "CourseModel",
        back_populates="author",
        cascade="all, delete-orphan",
    )
