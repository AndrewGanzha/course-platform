from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.exceptions import LectureNotFoundError


@dataclass(slots=True)
class DeleteLectureCommand:
    lecture_id: UUID


class DeleteLectureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: DeleteLectureCommand) -> None:
        async with self.uow:
            lection = await self.uow.lectures.get_by_id(command.lecture_id)

            if lection is None:
                raise LectureNotFoundError("Lecture not found")

            await self.uow.lectures.delete(command.lecture_id)
            await self.uow.commit()