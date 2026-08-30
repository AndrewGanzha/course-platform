from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.use_cases.answer_options.create_answer_option import (
    CreateAnswerOptionCommand,
    CreateAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.remove_answer_option import (
    RemoveAnswerOptionCommand,
    RemoveAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.update_answer_option import (
    UpdateAnswerOptionCommand,
    UpdateAnswerOptionUseCase,
)
from app.application.use_cases.questions.create_question import (
    CreateQuestionCommand,
    CreateQuestionUseCase,
)
from app.application.use_cases.questions.remove_question import (
    RemoveQuestionCommand,
    RemoveQuestionUseCase,
)
from app.application.use_cases.questions.update_question import (
    UpdateQuestionCommand,
    UpdateQuestionUseCase,
)
from app.domain.entities.user import User
from app.presentation.api.schemas import (
    AnswerOptionResponse,
    CreateAnswerOptionRequest,
    CreateQuestionRequest,
    ErrorResponse,
    QuestionResponse,
    UpdateAnswerOptionRequest,
    UpdateQuestionRequest,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    route_class=DishkaRoute,
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "Author or admin access is required.",
            "model": ErrorResponse,
        },
    },
)


@router.post(
    "/sections/{section_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create question",
    description="Creates a new interactive question inside the selected section.",
)
async def create_question(
    section_id: UUID,
    request: CreateQuestionRequest,
    actor: FromDishka[User],
    use_case: FromDishka[CreateQuestionUseCase],
) -> QuestionResponse:
    result = await use_case.execute(
        CreateQuestionCommand(
            actor=actor,
            section_id=section_id,
            text=request.text,
            position=request.position,
            question_type=request.question_type,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
        )
    )
    return QuestionResponse.model_validate(result)


@router.put(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Update question",
    description="Updates an existing question if it can still be changed safely.",
)
async def update_question(
    question_id: UUID,
    request: UpdateQuestionRequest,
    actor: FromDishka[User],
    use_case: FromDishka[UpdateQuestionUseCase],
) -> QuestionResponse:
    result = await use_case.execute(
        UpdateQuestionCommand(
            actor=actor,
            question_id=question_id,
            text=request.text,
            position=request.position,
            question_type=request.question_type,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
        )
    )
    return QuestionResponse.model_validate(result)


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove question",
    description="Removes an unused question from its section.",
)
async def remove_question(
    question_id: UUID,
    actor: FromDishka[User],
    use_case: FromDishka[RemoveQuestionUseCase],
) -> Response:
    await use_case.execute(
        RemoveQuestionCommand(actor=actor, question_id=question_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/questions/{question_id}/answer-options",
    response_model=AnswerOptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create answer option",
    description="Adds a new answer option to the selected question.",
)
async def create_answer_option(
    question_id: UUID,
    request: CreateAnswerOptionRequest,
    actor: FromDishka[User],
    use_case: FromDishka[CreateAnswerOptionUseCase],
) -> AnswerOptionResponse:
    result = await use_case.execute(
        CreateAnswerOptionCommand(
            actor=actor,
            question_id=question_id,
            text=request.text,
            position=request.position,
            is_correct=request.is_correct,
        )
    )
    return AnswerOptionResponse.model_validate(result)


@router.put(
    "/answer-options/{answer_option_id}",
    response_model=AnswerOptionResponse,
    summary="Update answer option",
    description=(
        "Updates an existing answer option if the question was not used yet."
    ),
)
async def update_answer_option(
    answer_option_id: UUID,
    request: UpdateAnswerOptionRequest,
    actor: FromDishka[User],
    use_case: FromDishka[UpdateAnswerOptionUseCase],
) -> AnswerOptionResponse:
    result = await use_case.execute(
        UpdateAnswerOptionCommand(
            actor=actor,
            answer_option_id=answer_option_id,
            text=request.text,
            position=request.position,
            is_correct=request.is_correct,
        )
    )
    return AnswerOptionResponse.model_validate(result)


@router.delete(
    "/answer-options/{answer_option_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove answer option",
    description=(
        "Removes an answer option if the question remains valid and was not used yet."
    ),
)
async def remove_answer_option(
    answer_option_id: UUID,
    actor: FromDishka[User],
    use_case: FromDishka[RemoveAnswerOptionUseCase],
) -> Response:
    await use_case.execute(
        RemoveAnswerOptionCommand(
            actor=actor,
            answer_option_id=answer_option_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
