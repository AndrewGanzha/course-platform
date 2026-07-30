from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from app.application.interfaces.services.password_hasher import PasswordHasher
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher

from app.application.use_cases.courses.get_course import GetCourseUseCase
from app.application.use_cases.courses.get_course_structure import GetCourseStructureUseCase
from app.application.use_cases.courses.get_courses import GetCoursesUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureUseCase
from app.application.use_cases.courses.create_course import CreateCourseUseCase
from app.application.use_cases.courses.update_course import UpdateCourseUseCase
from app.application.use_cases.lectures.create_lecture import CreateLectureUseCase
from app.application.use_cases.lectures.update_lecture import UpdateLectureUseCase
from app.application.use_cases.modules.create_module import CreateModuleUseCase
from app.application.use_cases.modules.update_module import UpdateModuleUseCase
from app.application.use_cases.sections.create_section import CreateSectionUseCase
from app.application.use_cases.sections.update_section import UpdateSectionUseCase
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
    def get_create_course_use_case(self) -> CreateCourseUseCase:
        return CreateCourseUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_update_course_use_case(self) -> UpdateCourseUseCase:
        return UpdateCourseUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_create_module_use_case(self) -> CreateModuleUseCase:
        return CreateModuleUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_update_module_use_case(self) -> UpdateModuleUseCase:
        return UpdateModuleUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_create_section_use_case(self) -> CreateSectionUseCase:
        return CreateSectionUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_update_section_use_case(self) -> UpdateSectionUseCase:
        return UpdateSectionUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_create_lecture_use_case(self) -> CreateLectureUseCase:
        return CreateLectureUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def get_update_lecture_use_case(self) -> UpdateLectureUseCase:
        return UpdateLectureUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        )

    @provide
    def provide_get_lecture_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetLectureUseCase:
        return GetLectureUseCase(lecture_repository=uow.lectures)

    @provide
    def get_password_hasher(self) -> PasswordHasher:
        return PwdlibPasswordHasher()

    @provide
    def get_register_user_use_case(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
            password_hasher=self.get_password_hasher(),
        )