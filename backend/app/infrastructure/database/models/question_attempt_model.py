from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class QuestionAttemptModel(Base):
    __tablename__ = "question_attempts"
    __table_args__ = (
        Index(
            "ix_question_attempts_student_question_number",
            "student_id",
            "question_id",
            "attempt_number",
        ),
        Index(
            "ix_question_attempts_question_student_number",
            "question_id",
            "student_id",
            "attempt_number",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    question_id: Mapped[str] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    student_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    attempt_number: Mapped[int] = mapped_column(Integer)
    selected_option_ids: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
    )
    result_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    awarded_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    question = relationship("QuestionModel", back_populates="attempts")
