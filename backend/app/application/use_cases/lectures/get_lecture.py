from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import LectureNotFoundError
from app.application.interfaces.repositories.lecture_repository import LectureRepository
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.lecture import Lecture
from app.domain.entities.user import User


@dataclass(slots=True)
class GetLectureQuery:
    lecture_id: UUID
    actor: User | None = None


class GetLectureUseCase:
    def __init__(
        self,
        lecture_repository: LectureRepository,
        access_service: CourseContentAccessService,
    ) -> None:
        self.lecture_repository = lecture_repository
        self.access_service = access_service

    async def execute(self, query: GetLectureQuery) -> Lecture:
        lecture = await self.lecture_repository.get_by_id(query.lecture_id)
        if lecture is None:
            raise LectureNotFoundError("Lecture not found.")

        can_view = await self.access_service.can_view_section_content(
            section_id=lecture.section_id,
            actor=query.actor,
        )
        if not can_view:
            raise LectureNotFoundError("Lecture not found.")

        return lecture
