from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.lecture_comments import LectureCommentDTO
from app.application.exceptions import LectureNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.lecture_comment import LectureComment
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateLectureCommentCommand:
    actor: User
    lecture_id: UUID
    text: str


class CreateLectureCommentUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        access_service: CourseContentAccessService,
    ) -> None:
        self.uow = uow
        self.access_service = access_service

    async def execute(self, command: CreateLectureCommentCommand) -> LectureCommentDTO:
        if not command.actor.is_student():
            raise PermissionDeniedError("Only students can leave lecture comments.")

        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(command.lecture_id)
            if lecture is None:
                raise LectureNotFoundError("Lecture not found.")

            can_view = await self.access_service.can_view_section_content(
                section_id=lecture.section_id,
                actor=command.actor,
            )
            if not can_view:
                raise PermissionDeniedError("User cannot comment on this lecture.")

            comment = LectureComment(
                id=uuid4(),
                lecture_id=lecture.id,
                user_id=command.actor.id,
                text=command.text,
                created_at=datetime.now(UTC),
            )
            await self.uow.lecture_comments.add(comment)
            await self.uow.commit()

            return LectureCommentDTO(
                id=comment.id,
                lecture_id=comment.lecture_id,
                user_id=comment.user_id,
                text=comment.text,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
