from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.application.use_cases.courses.get_course import GetCourseQuery, GetCourseUseCase
from app.application.use_cases.courses.get_course_structure import (
    GetCourseStructureQuery,
    GetCourseStructureUseCase,
)
from app.application.use_cases.courses.get_courses import GetCoursesQuery, GetCoursesUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureQuery, GetLectureUseCase
from app.presentation.api.schemas import (
    CourseListItemResponse,
    CourseResponse,
    CourseStructureResponse,
    LectureResponse,
)

router = APIRouter(tags=["Content"], route_class=DishkaRoute)


@router.get(
    "/courses",
    response_model=list[CourseListItemResponse],
)
async def get_courses(
    use_case: FromDishka[GetCoursesUseCase],
) -> list[CourseListItemResponse]:
    result = await use_case.execute(GetCoursesQuery())
    return [CourseListItemResponse.model_validate(course) for course in result]


@router.get(
    "/courses/{course_id}",
    response_model=CourseResponse,
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
)
async def get_lecture(
    lecture_id: UUID,
    use_case: FromDishka[GetLectureUseCase],
) -> LectureResponse:
    result = await use_case.execute(GetLectureQuery(lecture_id=lecture_id))
    return LectureResponse.model_validate(result)
