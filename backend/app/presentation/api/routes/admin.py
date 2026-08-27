from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.use_cases.courses.create_course import (
    CreateCourseCommand,
    CreateCourseUseCase,
)
from app.application.use_cases.courses.remove_course import (
    RemoveCourseCommand,
    RemoveCourseUseCase,
)
from app.application.use_cases.courses.update_course import (
    UpdateCourseCommand,
    UpdateCourseUseCase,
)
from app.application.use_cases.lectures.create_lecture import (
    CreateLectureCommand,
    CreateLectureUseCase,
)
from app.application.use_cases.lectures.remove_lecture import (
    RemoveLectureCommand,
    RemoveLectureUseCase,
)
from app.application.use_cases.lectures.update_lecture import (
    UpdateLectureCommand,
    UpdateLectureUseCase,
)
from app.application.use_cases.modules.create_module import (
    CreateModuleCommand,
    CreateModuleUseCase,
)
from app.application.use_cases.modules.remove_module import (
    RemoveModuleCommand,
    RemoveModuleUseCase,
)
from app.application.use_cases.modules.update_module import (
    UpdateModuleCommand,
    UpdateModuleUseCase,
)
from app.application.use_cases.sections.create_section import (
    CreateSectionCommand,
    CreateSectionUseCase,
)
from app.application.use_cases.sections.remove_section import (
    RemoveSectionCommand,
    RemoveSectionUseCase,
)
from app.application.use_cases.sections.update_section import (
    UpdateSectionCommand,
    UpdateSectionUseCase,
)
from app.domain.entities.user import User
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
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
    description=(
            "Creates a new course in the administrative API. "
            "The course is the root entity of the content tree."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
    },
)
async def create_course(
    request: CreateCourseRequest,
    actor: FromDishka[User],
    use_case: FromDishka[CreateCourseUseCase],
) -> CourseResponse:
    result = await use_case.execute(
        CreateCourseCommand(
            actor=actor,
            title=request.title,
            description=request.description,
        )
    )
    return CourseResponse.model_validate(result)

@router.put(
    "/courses/{course_id}",
    response_model=CourseResponse,
    summary="Update course",
    description=(
            "Updates an existing course by its identifier. "
            "Allows changing the course title and description."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_course(
    course_id: UUID,
    request: UpdateCourseRequest,
    actor: FromDishka[User],
    use_case: FromDishka[UpdateCourseUseCase],
) -> CourseResponse:
    result = await use_case.execute(
        UpdateCourseCommand(
            actor=actor,
            course_id=course_id,
            title=request.title,
            description=request.description,
        )
    )
    return CourseResponse.model_validate(result)


@router.delete(
    "/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove course",
    description="Removes a course and all of its content.",
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def remove_course(
    course_id: UUID,
    actor: FromDishka[User],
    use_case: FromDishka[RemoveCourseUseCase],
) -> Response:
    await use_case.execute(
        RemoveCourseCommand(actor=actor, course_id=course_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/courses/{course_id}/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create module",
    description=(
            "Creates a new module inside an existing course. "
            "Modules are used to group sections within a course."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_module(
    course_id: UUID,
    request: CreateModuleRequest,
    actor: FromDishka[User],
    use_case: FromDishka[CreateModuleUseCase],
) -> ModuleResponse:
    result = await use_case.execute(
        CreateModuleCommand(
            actor=actor,
            course_id=course_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )

    return ModuleResponse.model_validate(result)

@router.put(
    "/modules/{module_id}",
    response_model=ModuleResponse,
    summary="Update module",
    description=(
            "Updates an existing module by its identifier. "
            "Allows changing the module title, description and position."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_module(
    module_id: UUID,
    request: UpdateModuleRequest,
    actor: FromDishka[User],
    use_case: FromDishka[UpdateModuleUseCase],
) -> ModuleResponse:
    result = await use_case.execute(
        UpdateModuleCommand(
            actor=actor,
            module_id=module_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return ModuleResponse.model_validate(result)


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove module",
    description="Removes a module and all of its sections and lectures.",
    responses={
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def remove_module(
    module_id: UUID,
    actor: FromDishka[User],
    use_case: FromDishka[RemoveModuleUseCase],
) -> Response:
    await use_case.execute(
        RemoveModuleCommand(actor=actor, module_id=module_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/modules/{module_id}/sections",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create section",
    description=(
            "Creates a new section inside an existing module. "
            "Sections are used to group lectures within a module."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_section(
    module_id: UUID,
    request: CreateSectionRequest,
    actor: FromDishka[User],
    use_case: FromDishka[CreateSectionUseCase],
) -> SectionResponse:
    result = await use_case.execute(
        CreateSectionCommand(
            actor=actor,
            module_id=module_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )

    return SectionResponse.model_validate(result)

@router.put(
    "/sections/{section_id}",
    response_model=SectionResponse,
    description=(
            "Updates an existing section by its identifier. "
            "Allows changing the section title, description and position."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },

)
async def update_section(
    section_id: UUID,
    request: UpdateSectionRequest,
    actor: FromDishka[User],
    use_case: FromDishka[UpdateSectionUseCase],
) -> SectionResponse:
    result = await use_case.execute(
        UpdateSectionCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )

    return SectionResponse.model_validate(result)


@router.delete(
    "/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove section",
    description="Removes a section and all of its lectures.",
    responses={
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def remove_section(
    section_id: UUID,
    actor: FromDishka[User],
    use_case: FromDishka[RemoveSectionUseCase],
) -> Response:
    await use_case.execute(
        RemoveSectionCommand(actor=actor, section_id=section_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sections/{section_id}/lectures",
    response_model=LectureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lecture",
    description=(
            "Creates a new lecture inside an existing section. "
            "A lecture is the final content item in the course tree."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_lecture(
    section_id: UUID,
    request: CreateLectureRequest,
    actor: FromDishka[User],
    use_case: FromDishka[CreateLectureUseCase],
) -> LectureResponse:
    result = await use_case.execute(
        CreateLectureCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            content=request.content,
            position=request.position,
        )
    )

    return LectureResponse.model_validate(result)

@router.put(
    "/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="Update lecture",
    description=(
            "Updates an existing lecture by its identifier. "
            "Allows changing the lecture title, content and position."
    ),
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_lecture(
    lecture_id: UUID,
    request: UpdateLectureRequest,
    actor: FromDishka[User],
    use_case: FromDishka[UpdateLectureUseCase],
) -> LectureResponse:
    result = await use_case.execute(
        UpdateLectureCommand(
            actor=actor,
            lecture_id=lecture_id,
            title=request.title,
            content=request.content,
            position=request.position,
        )
    )

    return LectureResponse.model_validate(result)


@router.delete(
    "/lectures/{lecture_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Remove lecture",
    description="Removes a lecture by its identifier.",
    responses={
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def remove_lecture(
    lecture_id: UUID,
    actor: FromDishka[User],
    use_case: FromDishka[RemoveLectureUseCase],
) -> Response:
    await use_case.execute(
        RemoveLectureCommand(actor=actor, lecture_id=lecture_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
