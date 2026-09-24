from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.application.use_cases.code_tasks.get_code_task import (
    GetCodeTaskQuery,
    GetCodeTaskUseCase,
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
from app.application.use_cases.lectures.get_lecture import (
    GetLectureQuery,
    GetLectureUseCase,
)
from app.application.use_cases.questions.get_question import (
    GetQuestionQuery,
    GetQuestionUseCase,
)
from app.application.use_cases.tasks.get_task import GetTaskQuery, GetTaskUseCase
from app.presentation.api.schemas import (
    CodeTaskDetailsResponse,
    CourseListItemResponse,
    CourseResponse,
    CourseStructureResponse,
    LectureResponse,
    QuestionDetailsResponse,
    TaskDetailsResponse,
)
from app.presentation.api.schemas.errors import ErrorResponse

router = APIRouter(tags=["Content"], route_class=DishkaRoute)


@router.get(
    "/courses",
    response_model=list[CourseListItemResponse],
    summary="List available courses",
    description="Returns a public list of courses available in the system.",
)
async def get_courses(
    use_case: FromDishka[GetCoursesUseCase],
) -> list[CourseListItemResponse]:
    result = await use_case.execute(GetCoursesQuery())
    return [CourseListItemResponse.model_validate(course) for course in result]


@router.get(
    "/courses/{course_id}",
    response_model=CourseResponse,
    summary="Get course by ID",
    description="Returns a single course by its identifier.",
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_course(
    course_id: UUID,
    use_case: FromDishka[GetCourseUseCase],
) -> CourseResponse:
    result = await use_case.execute(GetCourseQuery(course_id=course_id))
    return CourseResponse.model_validate(result)


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
    use_case: FromDishka[GetCourseStructureUseCase],
) -> CourseStructureResponse:
    result = await use_case.execute(GetCourseStructureQuery(course_id=course_id))
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
    use_case: FromDishka[GetLectureUseCase],
) -> LectureResponse:
    result = await use_case.execute(GetLectureQuery(lecture_id=lecture_id))
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
    use_case: FromDishka[GetQuestionUseCase],
) -> QuestionDetailsResponse:
    result = await use_case.execute(GetQuestionQuery(question_id=question_id))
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
    use_case: FromDishka[GetTaskUseCase],
) -> TaskDetailsResponse:
    result = await use_case.execute(GetTaskQuery(task_id=task_id))
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
    use_case: FromDishka[GetCodeTaskUseCase],
) -> CodeTaskDetailsResponse:
    result = await use_case.execute(GetCodeTaskQuery(code_task_id=code_task_id))
    return CodeTaskDetailsResponse.model_validate(result)
