from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import AnswerOptionNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateAnswerOptionCommand:
    actor: User
    answer_option_id: UUID
    text: str
    position: int
    is_correct: bool


class UpdateAnswerOptionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: UpdateAnswerOptionCommand) -> AnswerOption:
        if not command.actor.can_manage_interactive_content():
            raise PermissionDeniedError('User cannot manage interactive content.')

        async with self.uow:
            answer_option = await self.uow.answer_options.get_by_id(command.answer_option_id)
            if answer_option is None:
                raise AnswerOptionNotFoundError('Answer option not found.')

            answer_option.update(
                text=command.text,
                position=command.position,
                is_correct=command.is_correct,
            )
            await self.uow.answer_options.update(answer_option)
            await self.uow.commit()
            return answer_option