from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.course import Course
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateCourseCommand:
    actor: User
    course_id: UUID
    title: str
    description: str


class UpdateCourseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateCourseCommand) -> Course:
        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=command.actor,
                course_id=command.course_id,
            )

            course.update(title=command.title, description=command.description)
            await self.uow.courses.update(course)
            await self.uow.commit()
            return course
