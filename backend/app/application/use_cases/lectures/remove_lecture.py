from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import LectureNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork


@dataclass(slots=True)
class RemoveLectureCommand:
    lecture_id: UUID


class RemoveLectureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: RemoveLectureCommand) -> None:
        async with self.uow:
            lecture = await self.uow.lectures.get_by_id(command.lecture_id)

            if lecture is None:
                raise LectureNotFoundError("Lecture not found")

            await self.uow.lectures.remove(command.lecture_id)
            await self.uow.commit()
