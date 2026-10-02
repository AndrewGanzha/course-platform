from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.dto.authenticated_user import AuthenticatedUser
from app.application.use_cases.code_tasks.get_code_task import (
    GetCodeTaskQuery,
    GetCodeTaskUseCase,
)
from app.application.use_cases.course_reviews.get_course_reviews import (
    GetCourseReviewsQuery,
    GetCourseReviewsUseCase,
)
from app.application.use_cases.course_reviews.upsert_course_review import (
    UpsertCourseReviewCommand,
    UpsertCourseReviewUseCase,
)
from app.application.use_cases.courses.get_course import (
    GetCourseQuery,
    GetCourseUseCase,
)
from app.application.use_cases.courses.get_course_structure import (
    GetCourseStructureQuery,
    GetCourseStructureUseCase,
)
from app.application.use_cases.courses.get_courses import (
    GetCoursesQuery,
    GetCoursesUseCase,
)
from app.application.use_cases.lecture_comments.create_lecture_comment import (
    CreateLectureCommentCommand,
    CreateLectureCommentUseCase,
)
from app.application.use_cases.lecture_comments.delete_lecture_comment import (
    DeleteLectureCommentCommand,
    DeleteLectureCommentUseCase,
)
from app.application.use_cases.lecture_comments.get_lecture_comments import (
    GetLectureCommentsQuery,
    GetLectureCommentsUseCase,
)
from app.application.use_cases.lecture_comments.update_lecture_comment import (
    UpdateLectureCommentCommand,
    UpdateLectureCommentUseCase,
)
from app.application.use_cases.lectures.get_lecture import (
    GetLectureQuery,
    GetLectureUseCase,
)
from app.application.use_cases.questions.get_question import (
    GetQuestionQuery,
    GetQuestionUseCase,
)
from app.application.use_cases.tasks.get_task import GetTaskQuery, GetTaskUseCase
from app.domain.entities.course import CourseDifficulty
from app.domain.entities.user import User
from app.presentation.api.schemas import (
    CodeTaskDetailsResponse,
    CourseCatalogCardResponse,
    CourseCatalogItemResponse,
    CourseReviewResponse,
    CourseStructureResponse,
    CreateLectureCommentRequest,
    LectureCommentResponse,
    LectureResponse,
    QuestionDetailsResponse,
    TaskDetailsResponse,
    UpdateLectureCommentRequest,
    UpsertCourseReviewRequest,
)
from app.presentation.api.schemas.errors import ErrorResponse

router = APIRouter(tags=["Content"], route_class=DishkaRoute)


@router.get(
    "/courses",
    response_model=list[CourseCatalogItemResponse],
    summary="Get public course catalog",
    description="Returns published courses formatted for catalog listing.",
)
async def get_courses(
    use_case: FromDishka[GetCoursesUseCase],
    search: str = Query(default=""),
    difficulty: CourseDifficulty | None = Query(default=None),
    tag: list[str] = Query(default=[]),
) -> list[CourseCatalogItemResponse]:
    result = await use_case.execute(
        GetCoursesQuery(
            search=search,
            difficulty=difficulty,
            tag_names=list(tag),
        )
    )
    return [CourseCatalogItemResponse.model_validate(course) for course in result]


@router.get(
    "/courses/{course_id}",
    response_model=CourseCatalogCardResponse,
    summary="Get public course page",
    description="Returns a detailed course card for the catalog page.",
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_course(
    course_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetCourseUseCase],
) -> CourseCatalogCardResponse:
    result = await use_case.execute(
        GetCourseQuery(course_id=course_id, actor=current_user)
    )
    return CourseCatalogCardResponse.model_validate(result)


@router.get(
    "/courses/{course_id}/structure",
    response_model=CourseStructureResponse,
    summary="Get course structure",
    description=(
        "Returns the course navigation tree: modules, sections and lectures "
        "without full lecture content."
    ),
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_course_structure(
    course_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetCourseStructureUseCase],
) -> CourseStructureResponse:
    result = await use_case.execute(
        GetCourseStructureQuery(course_id=course_id, actor=current_user)
    )
    return CourseStructureResponse.model_validate(result)


@router.get(
    "/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="Get lecture by ID",
    description="Returns the full content of a single lecture.",
    responses={
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_lecture(
    lecture_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetLectureUseCase],
) -> LectureResponse:
    result = await use_case.execute(
        GetLectureQuery(lecture_id=lecture_id, actor=current_user)
    )
    return LectureResponse.model_validate(result)


@router.get(
    "/questions/{question_id}",
    response_model=QuestionDetailsResponse,
    summary="Get question by ID",
    description="Returns the content of a single question with public answer options.",
    responses={
        404: {
            "description": "Question was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_question(
    question_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetQuestionUseCase],
) -> QuestionDetailsResponse:
    result = await use_case.execute(
        GetQuestionQuery(question_id=question_id, actor=current_user)
    )
    return QuestionDetailsResponse.model_validate(result)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskDetailsResponse,
    summary="Get task by ID",
    description="Returns the content of a single task without author check configuration.",
    responses={
        404: {
            "description": "Task was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_task(
    task_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetTaskUseCase],
) -> TaskDetailsResponse:
    result = await use_case.execute(GetTaskQuery(task_id=task_id, actor=current_user))
    return TaskDetailsResponse.model_validate(result)


@router.get(
    "/code-tasks/{code_task_id}",
    response_model=CodeTaskDetailsResponse,
    summary="Get code task by ID",
    description=(
        "Returns the content of a single code task and its editor configuration."
    ),
    responses={
        404: {
            "description": "Code task was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_code_task(
    code_task_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetCodeTaskUseCase],
) -> CodeTaskDetailsResponse:
    result = await use_case.execute(
        GetCodeTaskQuery(code_task_id=code_task_id, actor=current_user)
    )
    return CodeTaskDetailsResponse.model_validate(result)


@router.get(
    "/courses/{course_id}/reviews",
    response_model=list[CourseReviewResponse],
    summary="Get course reviews",
    description="Returns public reviews for a published course.",
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_course_reviews(
    course_id: UUID,
    use_case: FromDishka[GetCourseReviewsUseCase],
) -> list[CourseReviewResponse]:
    result = await use_case.execute(GetCourseReviewsQuery(course_id=course_id))
    return [CourseReviewResponse.model_validate(review) for review in result]


@router.put(
    "/courses/{course_id}/reviews/me",
    response_model=CourseReviewResponse,
    summary="Create or update my course review",
    description=(
        "Creates or updates the current student review after at least "
        "80% of the course sections have been completed."
    ),
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": (
                "Only a student who completed at least 80% of the course "
                "can create or update a review."
            ),
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def upsert_my_course_review(
    course_id: UUID,
    request: UpsertCourseReviewRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[UpsertCourseReviewUseCase],
) -> CourseReviewResponse:
    result = await use_case.execute(
        UpsertCourseReviewCommand(
            actor=actor,
            course_id=course_id,
            rating=request.rating,
            text=request.text,
        )
    )
    return CourseReviewResponse.model_validate(result)


@router.get(
    "/lectures/{lecture_id}/comments",
    response_model=list[LectureCommentResponse],
    summary="Get lecture comments",
    description="Returns discussion comments for a lecture visible to the user.",
    responses={
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot view comments of this lecture.",
            "model": ErrorResponse,
        },
    },
)
async def get_lecture_comments(
    lecture_id: UUID,
    current_user: FromDishka[User | None],
    use_case: FromDishka[GetLectureCommentsUseCase],
) -> list[LectureCommentResponse]:
    result = await use_case.execute(
        GetLectureCommentsQuery(lecture_id=lecture_id, actor=current_user)
    )
    return [LectureCommentResponse.model_validate(comment) for comment in result]


@router.post(
    "/lectures/{lecture_id}/comments",
    response_model=LectureCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lecture comment",
    description=(
        "Creates a comment under a lecture accessible to the current student."
    ),
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": (
                "Only a student who can access the lecture can leave a comment."
            ),
            "model": ErrorResponse,
        },
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_lecture_comment(
    lecture_id: UUID,
    request: CreateLectureCommentRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[CreateLectureCommentUseCase],
) -> LectureCommentResponse:
    result = await use_case.execute(
        CreateLectureCommentCommand(
            actor=actor,
            lecture_id=lecture_id,
            text=request.text,
        )
    )
    return LectureCommentResponse.model_validate(result)


@router.patch(
    "/comments/{comment_id}",
    response_model=LectureCommentResponse,
    summary="Update my lecture comment",
    description="Updates the text of a comment authored by the current user.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "Only the comment author can edit this comment.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Lecture comment was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_lecture_comment(
    comment_id: UUID,
    request: UpdateLectureCommentRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[UpdateLectureCommentUseCase],
) -> LectureCommentResponse:
    result = await use_case.execute(
        UpdateLectureCommentCommand(
            actor=actor,
            comment_id=comment_id,
            text=request.text,
        )
    )
    return LectureCommentResponse.model_validate(result)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete lecture comment",
    description=(
        "Deletes a comment. Allowed for its author, the author of the "
        "owning course, or a platform administrator."
    ),
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot delete this lecture comment.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Lecture comment was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_lecture_comment(
    comment_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[DeleteLectureCommentUseCase],
) -> Response:
    await use_case.execute(
        DeleteLectureCommentCommand(actor=actor, comment_id=comment_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
