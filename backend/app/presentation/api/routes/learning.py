from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.dto.authenticated_user import AuthenticatedUser
from app.application.use_cases.code_submissions.get_code_submission import (
    GetCodeSubmissionCommand,
    GetCodeSubmissionUseCase,
)
from app.application.use_cases.code_submissions.list_code_submissions import (
    ListCodeSubmissionsCommand,
    ListCodeSubmissionsUseCase,
)
from app.application.use_cases.code_submissions.submit_code_submission import (
    SubmitCodeSubmissionCommand,
    SubmitCodeSubmissionUseCase,
)
from app.application.use_cases.question_attempts.get_question_attempt_result import (
    GetQuestionAttemptResultCommand,
    GetQuestionAttemptResultUseCase,
)
from app.application.use_cases.question_attempts.start_question_attempt import (
    StartQuestionAttemptCommand,
    StartQuestionAttemptUseCase,
)
from app.application.use_cases.question_attempts.submit_question_answer import (
    SubmitQuestionAnswerCommand,
    SubmitQuestionAnswerUseCase,
)
from app.application.use_cases.task_attempts.submit_task_answer import (
    SubmitTaskAnswerCommand,
    SubmitTaskAnswerUseCase,
)
from app.presentation.api.schemas import (
    CodeSubmissionResponse,
    ErrorResponse,
    QuestionAttemptResultResponse,
    StartQuestionAttemptResponse,
    SubmitCodeSubmissionRequest,
    SubmitQuestionAnswerRequest,
    SubmitTaskAnswerRequest,
    TaskAttemptResponse,
)

router = APIRouter(
    prefix="/learning",
    tags=["Learning"],
    route_class=DishkaRoute,
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot perform this learning action.",
            "model": ErrorResponse,
        },
    },
)


@router.get(
    "/questions/{question_id}/attempt",
    response_model=StartQuestionAttemptResponse,
    summary="Get question attempt context",
    description="Returns all data required before the student submits a new answer.",
)
async def start_question_attempt(
    question_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[StartQuestionAttemptUseCase],
) -> StartQuestionAttemptResponse:
    result = await use_case.execute(
        StartQuestionAttemptCommand(
            actor=actor,
            question_id=question_id,
        )
    )
    return StartQuestionAttemptResponse.model_validate(result)


@router.post(
    "/questions/{question_id}/attempts",
    response_model=QuestionAttemptResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit question answer",
    description="Creates a new question attempt and immediately applies the result.",
)
async def submit_question_answer(
    question_id: UUID,
    request: SubmitQuestionAnswerRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[SubmitQuestionAnswerUseCase],
) -> QuestionAttemptResultResponse:
    result = await use_case.execute(
        SubmitQuestionAnswerCommand(
            actor=actor,
            question_id=question_id,
            selected_option_ids=request.selected_option_ids,
        )
    )
    return QuestionAttemptResultResponse(
        attempt_id=result.id,
        question_id=result.question_id,
        attempt_number=result.attempt_number,
        result_status=result.result_status,
        awarded_points=result.awarded_points,
        checked_at=result.checked_at,
        selected_option_ids=list(result.selected_option_ids),
    )


@router.get(
    "/attempts/{attempt_id}/result",
    response_model=QuestionAttemptResultResponse,
    summary="Get question attempt result",
    description="Returns a previously stored result of the selected question attempt.",
)
async def get_question_attempt_result(
    attempt_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[GetQuestionAttemptResultUseCase],
) -> QuestionAttemptResultResponse:
    result = await use_case.execute(
        GetQuestionAttemptResultCommand(
            actor=actor,
            attempt_id=attempt_id,
        )
    )
    return QuestionAttemptResultResponse.model_validate(result)


@router.post(
    "/tasks/{task_id}/attempts",
    response_model=TaskAttemptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit task answer",
    description="Creates a task attempt and immediately returns its result.",
)
async def submit_task_answer(
    task_id: UUID,
    request: SubmitTaskAnswerRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[SubmitTaskAnswerUseCase],
) -> TaskAttemptResponse:
    result = await use_case.execute(
        SubmitTaskAnswerCommand(
            actor=actor,
            task_id=task_id,
            submitted_answer=request.submitted_answer,
        )
    )
    return TaskAttemptResponse.model_validate(result)


@router.post(
    "/code-tasks/{code_task_id}/submissions",
    response_model=CodeSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit code solution",
    description="Creates a new code submission and hands it off to asynchronous checking.",
)
async def submit_code_submission(
    code_task_id: UUID,
    request: SubmitCodeSubmissionRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[SubmitCodeSubmissionUseCase],
) -> CodeSubmissionResponse:
    result = await use_case.execute(
        SubmitCodeSubmissionCommand(
            actor=actor,
            code_task_id=code_task_id,
            source_code=request.source_code,
        )
    )
    return CodeSubmissionResponse.model_validate(result)


@router.get(
    "/code-submissions/{submission_id}",
    response_model=CodeSubmissionResponse,
    summary="Get code submission status",
    description="Returns current status of the selected code submission.",
)
async def get_code_submission(
    submission_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[GetCodeSubmissionUseCase],
) -> CodeSubmissionResponse:
    result = await use_case.execute(
        GetCodeSubmissionCommand(
            actor=actor,
            submission_id=submission_id,
        )
    )
    return CodeSubmissionResponse.model_validate(result)


@router.get(
    "/code-tasks/{code_task_id}/submissions",
    response_model=list[CodeSubmissionResponse],
    summary="List code submission history",
    description="Returns submission history of the current student for the selected code task.",
)
async def list_code_submissions(
    code_task_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[ListCodeSubmissionsUseCase],
) -> list[CodeSubmissionResponse]:
    result = await use_case.execute(
        ListCodeSubmissionsCommand(
            actor=actor,
            code_task_id=code_task_id,
        )
    )
    return [CodeSubmissionResponse.model_validate(item) for item in result]
