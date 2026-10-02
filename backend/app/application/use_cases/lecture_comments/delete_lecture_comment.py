from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    LectureCommentNotFoundError,
    LectureNotFoundError,
    PermissionDeniedError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.lecture_course_resolver import LectureCourseResolver
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteLectureCommentCommand:
    actor: User
    comment_id: UUID


class DeleteLectureCommentUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        course_resolver: LectureCourseResolver,
    ) -> None:
        self.uow = uow
        self.course_resolver = course_resolver

    async def execute(self, command: DeleteLectureCommentCommand) -> None:
        async with self.uow:
            comment = await self.uow.lecture_comments.get_by_id(command.comment_id)
            if comment is None:
                raise LectureCommentNotFoundError("Lecture comment not found.")

            if not await self._can_delete(comment, command.actor):
                raise PermissionDeniedError("User cannot delete this lecture comment.")

            await self.uow.lecture_comments.delete(comment.id)
            await self.uow.commit()

    async def _can_delete(
        self,
        comment,
        actor: User,
    ) -> bool:
        if comment.is_written_by(actor.id):
            return True

        if actor.can_manage_platform():
            return True

        if actor.is_author():
            lecture = await self.uow.lectures.get_by_id(comment.lecture_id)
            if lecture is None:
                raise LectureNotFoundError("Lecture not found.")

            course = await self.course_resolver.resolve_course_for_section(
                lecture.section_id
            )
            return course.is_owned_by(actor.id)

        return False
