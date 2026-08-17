from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dto.authenticated_user import (
    AuthenticatedAdmin,
    AuthenticatedUser,
)
from app.application.interfaces.services.password_hasher import PasswordHasher
from app.application.interfaces.services.token_service import TokenService
from app.application.use_cases.answer_options.create_answer_option import (
    CreateAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.update_answer_option import (
    UpdateAnswerOptionUseCase,
)
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.courses.create_course import CreateCourseUseCase
from app.application.use_cases.courses.get_course import GetCourseUseCase
from app.application.use_cases.courses.get_course_structure import GetCourseStructureUseCase
from app.application.use_cases.courses.get_courses import GetCoursesUseCase
from app.application.use_cases.courses.remove_course import RemoveCourseUseCase
from app.application.use_cases.courses.update_course import UpdateCourseUseCase
from app.application.use_cases.lectures.create_lecture import CreateLectureUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureUseCase
from app.application.use_cases.lectures.remove_lecture import RemoveLectureUseCase
from app.application.use_cases.lectures.update_lecture import UpdateLectureUseCase
from app.application.use_cases.modules.create_module import CreateModuleUseCase
from app.application.use_cases.modules.remove_module import RemoveModuleUseCase
from app.application.use_cases.modules.update_module import UpdateModuleUseCase
from app.application.use_cases.questions.create_question import CreateQuestionUseCase
from app.application.use_cases.questions.update_question import UpdateQuestionUseCase
from app.application.use_cases.sections.create_section import CreateSectionUseCase
from app.application.use_cases.sections.remove_section import RemoveSectionUseCase
from app.application.use_cases.sections.update_section import UpdateSectionUseCase
from app.domain.entities.user import User
from app.infrastructure.database import SessionFactory, SqlAlchemyUnitOfWork
from app.infrastructure.security.jwt_token_service import (
    InvalidTokenError,
    JwtTokenService,
)
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.presentation.exceptions import AuthenticationError, PermissionDeniedError

http_bearer = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="BearerAuth",
    description="Enter JWT access token",
    auto_error=False,
)


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
    def get_create_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateCourseUseCase:
        return CreateCourseUseCase(uow=uow)

    @provide
    def get_update_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateCourseUseCase:
        return UpdateCourseUseCase(uow=uow)

    @provide
    def get_remove_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveCourseUseCase:
        return RemoveCourseUseCase(uow=uow)

    @provide
    def get_create_module_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateModuleUseCase:
        return CreateModuleUseCase(uow=uow)

    @provide
    def get_update_module_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateModuleUseCase:
        return UpdateModuleUseCase(uow=uow)

    @provide
    def get_remove_module_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveModuleUseCase:
        return RemoveModuleUseCase(uow=uow)

    @provide
    def get_create_section_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateSectionUseCase:
        return CreateSectionUseCase(uow=uow)

    @provide
    def get_update_section_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateSectionUseCase:
        return UpdateSectionUseCase(uow=uow)

    @provide
    def get_remove_section_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveSectionUseCase:
        return RemoveSectionUseCase(uow=uow)

    @provide
    def get_create_lecture_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateLectureUseCase:
        return CreateLectureUseCase(uow=uow)

    @provide
    def get_update_lecture_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateLectureUseCase:
        return UpdateLectureUseCase(uow=uow)

    @provide
    def get_remove_lecture_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveLectureUseCase:
        return RemoveLectureUseCase(uow=uow)

    @provide
    def get_create_question_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateQuestionUseCase:
        return CreateQuestionUseCase(uow=uow)

    @provide
    def get_update_question_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateQuestionUseCase:
        return UpdateQuestionUseCase(uow=uow)

    @provide
    def get_create_answer_option_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateAnswerOptionUseCase:
        return CreateAnswerOptionUseCase(uow=uow)

    @provide
    def get_update_answer_option_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateAnswerOptionUseCase:
        return UpdateAnswerOptionUseCase(uow=uow)

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
    def get_register_user_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        password_hasher: PasswordHasher,
    ) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            uow=uow,
            password_hasher=password_hasher,
        )

    @provide
    def get_login_user_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> LoginUserUseCase:
        return LoginUserUseCase(
            uow=uow,
            password_hasher=password_hasher,
            token_service=token_service,
        )

    @provide
    def get_token_service(self) -> TokenService:
        return JwtTokenService()

    @provide
    async def get_credentials(
        self,
        request: Request,
    ) -> HTTPAuthorizationCredentials | None:
        return await http_bearer(request)

    @provide
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials | None,
        uow: SqlAlchemyUnitOfWork,
        token_service: TokenService,
    ) -> AuthenticatedUser:
        if credentials is None:
            raise AuthenticationError(
                "Authentication credentials were not provided"
            )

        try:
            user_id = token_service.get_user_id(credentials.credentials)
        except InvalidTokenError as exc:
            raise AuthenticationError("Token is invalid or expired") from exc

        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise AuthenticationError("Authenticated user was not found")

        return AuthenticatedUser(user)

    @provide
    def get_current_admin(
        self,
        current_user: AuthenticatedUser,
    ) -> AuthenticatedAdmin:
        if not current_user.can_manage_platform():
            raise PermissionDeniedError("Admin access is required.")

        return AuthenticatedAdmin(current_user)

    @provide
    def get_current_author_or_admin(
        self,
        current_user: AuthenticatedUser
    ) -> User:
        if not current_user.can_manage_content():
            raise PermissionDeniedError("Author or admin access is required.")
        return current_user
