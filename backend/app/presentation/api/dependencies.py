from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from app.application.use_cases.courses.get_course import GetCourseUseCase
from app.application.use_cases.courses.get_course_structure import GetCourseStructureUseCase
from app.application.use_cases.courses.get_courses import GetCoursesUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureUseCase
from app.infrastructure.database import SessionFactory, SqlAlchemyUnitOfWork


class ApiProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_uow(
        self,
    ) -> AsyncIterator[SqlAlchemyUnitOfWork]:
        async with SqlAlchemyUnitOfWork(session_factory=SessionFactory) as uow:
            yield uow

    @provide
    def provide_get_courses_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetCoursesUseCase:
        return GetCoursesUseCase(
            course_repository=uow.courses,
        )

    @provide
    def provide_get_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetCourseUseCase:
        return GetCourseUseCase(
            course_repository=uow.courses,
        )

    @provide
    def provide_get_course_structure_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetCourseStructureUseCase:
        return GetCourseStructureUseCase(
            course_repository=uow.courses,
            module_repository=uow.modules,
            section_repository=uow.sections,
            lecture_repository=uow.lectures,
        )

    @provide
    def provide_get_lecture_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetLectureUseCase:
        return GetLectureUseCase(lecture_repository=uow.lectures)
