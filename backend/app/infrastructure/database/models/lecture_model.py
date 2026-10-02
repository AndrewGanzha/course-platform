from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class LectureModel(Base):
    __tablename__ = "lectures"
    __table_args__ = (
        Index(
            "ix_lectures_section_position",
            "section_id",
            "position",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    section_id: Mapped[str] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)

    section = relationship("SectionModel", back_populates="lectures")
