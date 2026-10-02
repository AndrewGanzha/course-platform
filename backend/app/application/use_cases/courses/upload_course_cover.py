from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CourseNotFoundError, PermissionDeniedError
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.storage.image_storage import ImageStorage
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.cover_image_policy import CoverImagePolicy
from app.domain.entities.course import Course
from app.domain.entities.user import User


@dataclass(slots=True)
class UploadCourseCoverCommand:
    actor: User
    course_id: UUID
    filename: str
    content_type: str | None
    content: bytes


class UploadCourseCoverUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        image_storage: ImageStorage,
        cover_image_policy: CoverImagePolicy,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.image_storage = image_storage
        self.cover_image_policy = cover_image_policy
        self.content_cache = content_cache

    async def execute(self, command: UploadCourseCoverCommand) -> Course:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None:
                raise CourseNotFoundError("Course not found.")

            if not command.actor.can_manage_platform() and not course.is_owned_by(
                command.actor.id
            ):
                raise PermissionDeniedError("User cannot manage this course.")

            self.cover_image_policy.validate(
                filename=command.filename,
                content_type=command.content_type,
                size=len(command.content),
            )

            cover_image_url = await self.image_storage.save(
                course_id=course.id,
                filename=command.filename,
                content=command.content,
            )
            course.change_cover_image(cover_image_url)
            await self.uow.courses.update(course)
            await self.uow.commit()

        if self.content_cache is not None:
            await self.content_cache.invalidate_course(command.course_id)

        return course
