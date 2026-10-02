from dataclasses import dataclass
from uuid import UUID

from app.application.dto.lecture_comments import LectureCommentDTO
from app.application.exceptions import (
    LectureCommentNotFoundError,
    PermissionDeniedError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateLectureCommentCommand:
    actor: User
    comment_id: UUID
    text: str


class UpdateLectureCommentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpdateLectureCommentCommand) -> LectureCommentDTO:
        async with self.uow:
            comment = await self.uow.lecture_comments.get_by_id(command.comment_id)
            if comment is None:
                raise LectureCommentNotFoundError("Lecture comment not found.")

            if not comment.is_written_by(command.actor.id):
                raise PermissionDeniedError(
                    "Only the author can edit this lecture comment."
                )

            comment.update(text=command.text)
            await self.uow.lecture_comments.update(comment)
            await self.uow.commit()

            return LectureCommentDTO(
                id=comment.id,
                lecture_id=comment.lecture_id,
                user_id=comment.user_id,
                text=comment.text,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
