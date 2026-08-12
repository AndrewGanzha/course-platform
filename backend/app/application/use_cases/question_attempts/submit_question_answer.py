from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import PermissionDeniedError, QuestionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.question_attempt import QuestionAttempt
from app.domain.entities.user import User


@dataclass(slots=True)
class SubmitQuestionAnswerCommand:
    actor: User
    question_id: UUID
    selected_option_ids: list[UUID]


class SubmitQuestionAnswerUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: SubmitQuestionAnswerCommand) -> QuestionAttempt:
        if not command.actor.can_take_learning_activities():
            raise PermissionDeniedError('User cannot submit question answers.')

        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError('Question not found.')

            answer_options = await self.uow.answer_options.get_by_ids(question.answer_option_ids)
            question.validate_answer_options_configuration(answer_options)

            attempts = await self.uow.question_attempts.get_by_student_and_question(
                student_id=command.actor.id,
                question_id=question.id,
            )
            has_correct_attempt = any(attempt.is_correct() for attempt in attempts)

            question.ensure_attempt_available(
                existing_attempts_count=len(attempts),
                has_correct_attempt=has_correct_attempt,
            )

            attempt = QuestionAttempt(
                id=uuid4(),
                question_id=question.id,
                student_id=command.actor.id,
                attempt_number=len(attempts) + 1,
                selected_option_ids=command.selected_option_ids,
            )

            result_status = question.resolve_result_status(
                selected_option_ids=attempt.selected_option_ids,
                answer_options=answer_options,
            )
            awarded_points = question.resolve_awarded_points(
                selected_option_ids=attempt.selected_option_ids,
                answer_options=answer_options,
            )

            attempt.apply_result(
                result_status=result_status,
                awarded_points=awarded_points,
            )

            await self.uow.question_attempts.add(attempt)
            await self.uow.commit()
            return attempt
