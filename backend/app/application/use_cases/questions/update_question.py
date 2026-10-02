from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    QuestionAlreadyUsedError,
    QuestionNotFoundError,
)
from app.application.interfaces.content_cache import ContentCache
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateQuestionCommand:
    actor: User
    question_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int


class UpdateQuestionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        content_cache: ContentCache | None = None,
    ) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)
        self.content_cache = content_cache

    async def execute(self, command: UpdateQuestionCommand) -> Question:
        course_id: UUID | None = None
        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError("Question not found.")

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=question.section_id,
            )

            has_attempts = await self.uow.question_attempts.exists_by_question_id(
                question.id
            )
            if has_attempts:
                raise QuestionAlreadyUsedError(
                    "Question already has student attempts and cannot be changed safely."
                )

            question.update(
                text=command.text,
                position=command.position,
                question_type=command.question_type,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
            )
            await self.uow.questions.update(question)
            await self.uow.commit()
            course_id = await self.course_access_service.resolve_course_id_for_section(
                question.section_id
            )

        if self.content_cache is not None and course_id is not None:
            await self.content_cache.invalidate_course(course_id)

        return question
