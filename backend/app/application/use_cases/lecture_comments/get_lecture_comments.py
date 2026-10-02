from dataclasses import dataclass
from uuid import UUID

from app.application.dto.lecture_comments import LectureCommentDTO
from app.application.exceptions import LectureNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class GetLectureCommentsQuery:
    lecture_id: UUID
    actor: User | None = None


class GetLectureCommentsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        access_service: CourseContentAccessService,
    ) -> None:
        self.uow = uow
        self.access_service = access_service

    async def execute(self, query: GetLectureCommentsQuery) -> list[LectureCommentDTO]:
        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(query.lecture_id)
            if lecture is None:
                raise LectureNotFoundError("Lecture not found.")

            can_view = await self.access_service.can_view_section_content(
                section_id=lecture.section_id,
                actor=query.actor,
            )
            if not can_view:
                raise PermissionDeniedError(
                    "User cannot view comments of this lecture."
                )

            comments = await self.uow.lecture_comments.list_by_lecture_id(lecture.id)
            return [
                LectureCommentDTO(
                    id=comment.id,
                    lecture_id=comment.lecture_id,
                    user_id=comment.user_id,
                    text=comment.text,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                )
                for comment in comments
            ]
