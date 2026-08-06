from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork


@dataclass(slots=True)
class RemoveCourseCommand:
    course_id: UUID


class RemoveCourseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: RemoveCourseCommand) -> None:
        async with self.uow:
            course = await self.uow.courses.get_by_id(command.course_id)

            if course is None:
                raise CourseNotFoundError("Course not found")
            await self.uow.courses.remove(course.id)
            await self.uow.commit()
