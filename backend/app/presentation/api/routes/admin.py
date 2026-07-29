from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.use_cases.courses.create_course import (
    CreateCourseCommand,
    CreateCourseUseCase,
)
from app.application.use_cases.courses.update_course import (
    UpdateCourseCommand,
    UpdateCourseUseCase,
)
from app.application.use_cases.lectures.create_lecture import (
    CreateLectureCommand,
    CreateLectureUseCase,
)
from app.application.use_cases.lectures.update_lecture import (
    UpdateLectureCommand,
    UpdateLectureUseCase,
)
from app.application.use_cases.modules.create_module import (
    CreateModuleCommand,
    CreateModuleUseCase,
)
from app.application.use_cases.modules.update_module import (
    UpdateModuleCommand,
    UpdateModuleUseCase,
)
from app.application.use_cases.sections.create_section import (
    CreateSectionCommand,
    CreateSectionUseCase,
)
from app.application.use_cases.sections.update_section import (
    UpdateSectionCommand,
    UpdateSectionUseCase,
)
from app.presentation.api.schemas import (
    CourseResponse,
    CreateCourseRequest,
    CreateLectureRequest,
    CreateModuleRequest,
    CreateSectionRequest,
    LectureResponse,
    ModuleResponse,
    SectionResponse,
    UpdateCourseRequest,
    UpdateLectureRequest,
    UpdateModuleRequest,
    UpdateSectionRequest,
    ErrorResponse,
)

router = APIRouter(prefix="/admin", tags=["Admin"], route_class=DishkaRoute)

@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
        request: CreateCourseRequest,
        use_case: FromDishka[CreateCourseUseCase]
) -> CourseResponse:
    result = await use_case.execute(
        CreateCourseCommand(title=request.title, description=request.description)
    )
    return CourseResponse.model_validate(result)

@router.post(
    "/courses/{course_id}",
    response_model=CourseResponse
)
async def update_course(
    course_id: UUID,
    request: UpdateCourseRequest,
    use_case: FromDishka[UpdateCourseUseCase]
) -> CourseResponse:
    result = await use_case.execute(
        UpdateCourseCommand(course_id=course_id, title=request.title, description=request.description)
    )
    return CourseResponse.model_validate(result)