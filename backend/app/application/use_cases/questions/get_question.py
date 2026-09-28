from dataclasses import dataclass
from uuid import UUID

from app.application.dto.question_details import (
    AnswerOptionDetailsDTO,
    QuestionDetailsDTO,
)
from app.application.exceptions import QuestionNotFoundError
from app.application.interfaces.repositories.answer_option_repository import (
    AnswerOptionRepository,
)
from app.application.interfaces.repositories.question_repository import (
    QuestionRepository,
)
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.domain.entities.user import User


@dataclass(slots=True)
class GetQuestionQuery:
    question_id: UUID
    actor: User | None = None


class GetQuestionUseCase:
    def __init__(
        self,
        question_repository: QuestionRepository,
        answer_option_repository: AnswerOptionRepository,
        access_service: CourseContentAccessService,
    ) -> None:
        self.question_repository = question_repository
        self.answer_option_repository = answer_option_repository
        self.access_service = access_service

    async def execute(self, query: GetQuestionQuery) -> QuestionDetailsDTO:
        question = await self.question_repository.get_by_id(query.question_id)
        if question is None:
            raise QuestionNotFoundError("Question not found.")

        can_view = await self.access_service.can_view_section_content(
            section_id=question.section_id,
            actor=query.actor,
        )
        if not can_view:
            raise QuestionNotFoundError("Question not found.")

        answer_options = await self.answer_option_repository.get_by_ids(
            question.answer_option_ids
        )
        option_dtos = [
            AnswerOptionDetailsDTO(
                id=option.id,
                text=option.text,
                position=option.position,
            )
            for option in sorted(answer_options, key=lambda item: item.position)
        ]

        return QuestionDetailsDTO(
            id=question.id,
            section_id=question.section_id,
            text=question.text,
            position=question.position,
            question_type=question.question_type,
            max_attempts=question.max_attempts,
            reward_points=question.reward_points,
            answer_options=option_dtos,
        )
