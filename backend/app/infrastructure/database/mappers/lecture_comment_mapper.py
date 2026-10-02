from uuid import UUID

from app.domain.entities.lecture_comment import LectureComment
from app.infrastructure.database.models.lecture_comment_model import LectureCommentModel


class LectureCommentMapper:
    @staticmethod
    def to_domain(model: LectureCommentModel) -> LectureComment:
        return LectureComment(
            id=UUID(model.id),
            lecture_id=UUID(model.lecture_id),
            user_id=UUID(model.user_id),
            text=model.text,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(comment: LectureComment) -> LectureCommentModel:
        return LectureCommentModel(
            id=str(comment.id),
            lecture_id=str(comment.lecture_id),
            user_id=str(comment.user_id),
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
