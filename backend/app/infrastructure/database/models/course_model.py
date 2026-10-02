from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class CourseModel(Base):
    __tablename__ = "courses"
    __table_args__ = (
        Index(
            "ix_courses_status_difficulty",
            "status",
            "difficulty",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    author_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    short_description: Mapped[str] = mapped_column(String(280), default="")
    difficulty: Mapped[str] = mapped_column(String(32), default="beginner")
    tag_names: Mapped[list[str]] = mapped_column(JSON, default=list)

    author = relationship("UserModel", back_populates="courses")
    modules = relationship(
        "ModuleModel",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="ModuleModel.position",
    )
