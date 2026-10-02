from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.application.dto.authenticated_user import AuthenticatedUser
from app.application.use_cases.profile.get_my_course_analytics import (
    GetMyCourseAnalyticsQuery,
    GetMyCourseAnalyticsUseCase,
)
from app.application.use_cases.profile.get_my_profile import (
    GetMyProfileQuery,
    GetMyProfileUseCase,
)
from app.application.use_cases.profile.get_my_teaching_course_analytics import (
    GetMyTeachingCourseAnalyticsQuery,
    GetMyTeachingCourseAnalyticsUseCase,
)
from app.application.use_cases.profile.update_my_profile import (
    UpdateMyProfileCommand,
    UpdateMyProfileUseCase,
)
from app.presentation.api.schemas import (
    AuthorCourseAnalyticsResponse,
    ErrorResponse,
    StudentCourseAnalyticsResponse,
    UpdateMyProfileRequest,
    UserProfileResponse,
)

router = APIRouter(prefix="/profile", tags=["Profile"], route_class=DishkaRoute)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get my profile",
    description="Returns the current authenticated user profile.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_profile(
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[GetMyProfileUseCase],
) -> UserProfileResponse:
    result = await use_case.execute(GetMyProfileQuery(actor=actor))
    return UserProfileResponse.model_validate(result)


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update my profile",
    description="Updates the current authenticated user profile.",
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
    },
)
async def update_my_profile(
    request: UpdateMyProfileRequest,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[UpdateMyProfileUseCase],
) -> UserProfileResponse:
    result = await use_case.execute(
        UpdateMyProfileCommand(
            actor=actor,
            full_name=request.full_name,
            bio=request.bio,
            avatar_url=(
                str(request.avatar_url) if request.avatar_url is not None else None
            ),
        )
    )
    return UserProfileResponse.model_validate(result)


@router.get(
    "/me/courses/{course_id}/analytics",
    response_model=StudentCourseAnalyticsResponse,
    summary="Get my course analytics",
    description=(
        "Returns learning analytics of the current student for the selected course."
    ),
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot view own learning analytics.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_course_analytics(
    course_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[GetMyCourseAnalyticsUseCase],
) -> StudentCourseAnalyticsResponse:
    result = await use_case.execute(
        GetMyCourseAnalyticsQuery(actor=actor, course_id=course_id)
    )
    return StudentCourseAnalyticsResponse.model_validate(result)


@router.get(
    "/me/teaching/courses/{course_id}/analytics",
    response_model=AuthorCourseAnalyticsResponse,
    summary="Get teaching analytics for my course",
    description=(
        "Returns aggregated teaching analytics for a course owned by the current author."
    ),
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "User cannot view teaching analytics for this course.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_my_teaching_course_analytics(
    course_id: UUID,
    actor: FromDishka[AuthenticatedUser],
    use_case: FromDishka[GetMyTeachingCourseAnalyticsUseCase],
) -> AuthorCourseAnalyticsResponse:
    result = await use_case.execute(
        GetMyTeachingCourseAnalyticsQuery(actor=actor, course_id=course_id)
    )
    return AuthorCourseAnalyticsResponse.model_validate(result)
