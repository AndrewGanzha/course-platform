from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import PermissionDeniedError, SectionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateQuestionCommand:
    actor: User
    section_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int


class CreateQuestionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: CreateQuestionCommand) -> Question:
        if not command.actor.can_manage_interactive_content():
            raise PermissionDeniedError('User cannot manage interactive content.')

        async with self.uow:
            section = await self.uow.sections.get_by_id(command.section_id)
            if section is None:
                raise SectionNotFoundError('Section not found.')

            question = Question(
                id=uuid4(),
                section_id=command.section_id,
                text=command.text,
                position=command.position,
                question_type=command.question_type,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
            )
            section.add_question(question.id)
            await self.uow.questions.add(question)
            await self.uow.sections.update(section)
            await self.uow.commit()
            return question