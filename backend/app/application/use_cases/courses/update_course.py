from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CourseNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.course import Course, CourseDifficulty
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateCourseCommand:
    actor: User
    course_id: UUID
    title: str
    description: str
    short_description: str = ""
    cover_image_url: str | None = None
    difficulty: CourseDifficulty = CourseDifficulty.BEGINNER
    tag_names: list[str] | None = None


class UpdateCourseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpdateCourseCommand) -> Course:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)
            if course is None:
                raise CourseNotFoundError("Course not found.")

            if not command.actor.can_manage_platform() and not course.is_owned_by(
                command.actor.id
            ):
                raise PermissionDeniedError("User cannot manage this course.")

            course.update(title=command.title, description=command.description)
            course.update_metadata(
                cover_image_url=command.cover_image_url,
                short_description=command.short_description,
                difficulty=command.difficulty,
                tag_names=list(command.tag_names or []),
            )
            await self.uow.courses.update(course)
            await self.uow.commit()
            return course
