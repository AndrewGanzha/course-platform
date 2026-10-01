from collections.abc import AsyncIterator
from pathlib import Path

from dishka import Provider, Scope, provide
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dto.authenticated_user import (
    AuthenticatedAdmin,
    AuthenticatedUser,
)
from app.application.interfaces.services.password_hasher import PasswordHasher
from app.application.interfaces.services.token_service import TokenService
from app.application.interfaces.storage.image_storage import ImageStorage
from app.application.interfaces.submission_queue import SubmissionQueue
from app.application.services.course_catalog_read_service import (
    CourseCatalogReadService,
)
from app.application.services.course_content_access_service import (
    CourseContentAccessService,
)
from app.application.services.cover_image_policy import CoverImagePolicy
from app.application.use_cases.answer_options.create_answer_option import (
    CreateAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.update_answer_option import (
    UpdateAnswerOptionUseCase,
)
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.code_submissions.get_code_submission import (
    GetCodeSubmissionUseCase,
)
from app.application.use_cases.code_submissions.list_code_submissions import (
    ListCodeSubmissionsUseCase,
)
from app.application.use_cases.code_submissions.submit_code_submission import (
    SubmitCodeSubmissionUseCase,
)
from app.application.use_cases.code_tasks.create_code_task import (
    CreateCodeTaskUseCase,
)
from app.application.use_cases.code_tasks.get_code_task import GetCodeTaskUseCase
from app.application.use_cases.code_tasks.remove_code_task import (
    RemoveCodeTaskUseCase,
)
from app.application.use_cases.code_tasks.update_code_task import (
    UpdateCodeTaskUseCase,
)
from app.application.use_cases.courses.archive_course import ArchiveCourseUseCase
from app.application.use_cases.courses.create_course import CreateCourseUseCase
from app.application.use_cases.courses.get_course import GetCourseUseCase
from app.application.use_cases.courses.get_course_publication_readiness import (
    GetCoursePublicationReadinessUseCase,
)
from app.application.use_cases.courses.get_course_structure import (
    GetCourseStructureUseCase,
)
from app.application.use_cases.courses.get_courses import GetCoursesUseCase
from app.application.use_cases.courses.publish_course import PublishCourseUseCase
from app.application.use_cases.courses.remove_course import RemoveCourseUseCase
from app.application.use_cases.courses.update_course import UpdateCourseUseCase
from app.application.use_cases.courses.upload_course_cover import (
    UploadCourseCoverUseCase,
)
from app.application.use_cases.lectures.create_lecture import CreateLectureUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureUseCase
from app.application.use_cases.lectures.remove_lecture import RemoveLectureUseCase
from app.application.use_cases.lectures.update_lecture import UpdateLectureUseCase
from app.application.use_cases.modules.create_module import CreateModuleUseCase
from app.application.use_cases.modules.remove_module import RemoveModuleUseCase
from app.application.use_cases.modules.update_module import UpdateModuleUseCase
from app.application.use_cases.profile.get_my_course_analytics import (
    GetMyCourseAnalyticsUseCase,
)
from app.application.use_cases.profile.get_my_profile import GetMyProfileUseCase
from app.application.use_cases.profile.update_my_profile import (
    UpdateMyProfileUseCase,
)
from app.application.use_cases.question_attempts.get_question_attempt_result import (
    GetQuestionAttemptResultUseCase,
)
from app.application.use_cases.question_attempts.start_question_attempt import (
    StartQuestionAttemptUseCase,
)
from app.application.use_cases.question_attempts.submit_question_answer import (
    SubmitQuestionAnswerUseCase,
)
from app.application.use_cases.questions.create_question import CreateQuestionUseCase
from app.application.use_cases.questions.get_question import GetQuestionUseCase
from app.application.use_cases.questions.update_question import UpdateQuestionUseCase
from app.application.use_cases.sections.create_section import CreateSectionUseCase
from app.application.use_cases.sections.remove_section import RemoveSectionUseCase
from app.application.use_cases.sections.update_section import UpdateSectionUseCase
from app.application.use_cases.task_attempts.submit_task_answer import (
    SubmitTaskAnswerUseCase,
)
from app.application.use_cases.tasks.create_task import CreateTaskUseCase
from app.application.use_cases.tasks.get_task import GetTaskUseCase
from app.application.use_cases.tasks.remove_task import RemoveTaskUseCase
from app.application.use_cases.tasks.update_task import UpdateTaskUseCase
from app.application.use_cases.test_cases.create_test_case import (
    CreateTestCaseUseCase,
)
from app.application.use_cases.test_cases.remove_test_case import (
    RemoveTestCaseUseCase,
)
from app.application.use_cases.test_cases.update_test_case import (
    UpdateTestCaseUseCase,
)
from app.bootstrap.build_submission_queue import build_submission_queue
from app.domain.entities.user import User
from app.infrastructure.config import get_settings
from app.infrastructure.database import SessionFactory, SqlAlchemyUnitOfWork
from app.infrastructure.security.jwt_token_service import (
    InvalidTokenError,
    JwtTokenService,
)
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.storage.local_image_storage import LocalImageStorage
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
    def get_course_content_access_service(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CourseContentAccessService:
        return CourseContentAccessService(
            course_repository=uow.courses,
            module_repository=uow.modules,
            section_repository=uow.sections,
        )

    @provide
    def get_course_catalog_read_service(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CourseCatalogReadService:
        return CourseCatalogReadService(
            module_repository=uow.modules,
            section_repository=uow.sections,
            lecture_repository=uow.lectures,
            question_repository=uow.questions,
            task_repository=uow.tasks,
            code_task_repository=uow.code_tasks,
        )

    @provide(scope=Scope.APP)
    def get_submission_queue(self) -> SubmissionQueue:
        return build_submission_queue()

    @provide
    def provide_get_courses_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        catalog_read_service: CourseCatalogReadService,
    ) -> GetCoursesUseCase:
        return GetCoursesUseCase(
            course_repository=uow.courses,
            catalog_read_service=catalog_read_service,
        )

    @provide
    def provide_get_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        access_service: CourseContentAccessService,
        catalog_read_service: CourseCatalogReadService,
    ) -> GetCourseUseCase:
        return GetCourseUseCase(
            course_repository=uow.courses,
            access_service=access_service,
            catalog_read_service=catalog_read_service,
        )

    @provide
    def provide_get_course_structure_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        access_service: CourseContentAccessService,
    ) -> GetCourseStructureUseCase:
        return GetCourseStructureUseCase(
            course_repository=uow.courses,
            module_repository=uow.modules,
            section_repository=uow.sections,
            lecture_repository=uow.lectures,
            task_repository=uow.tasks,
            code_task_repository=uow.code_tasks,
            access_service=access_service,
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
    def get_cover_image_policy(self) -> CoverImagePolicy:
        settings = get_settings()
        return CoverImagePolicy(
            max_size_bytes=settings.media.max_cover_image_bytes,
        )

    @provide
    def get_image_storage(self) -> ImageStorage:
        settings = get_settings()
        return LocalImageStorage(
            root=Path(settings.media.root),
            url_prefix=settings.media.url_prefix,
        )

    @provide
    def get_upload_course_cover_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        image_storage: ImageStorage,
        cover_image_policy: CoverImagePolicy,
    ) -> UploadCourseCoverUseCase:
        return UploadCourseCoverUseCase(
            uow=uow,
            image_storage=image_storage,
            cover_image_policy=cover_image_policy,
        )

    @provide
    def get_remove_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveCourseUseCase:
        return RemoveCourseUseCase(uow=uow)

    @provide
    def get_publish_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> PublishCourseUseCase:
        return PublishCourseUseCase(uow=uow)

    @provide
    def get_get_course_publication_readiness_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetCoursePublicationReadinessUseCase:
        return GetCoursePublicationReadinessUseCase(uow=uow)

    @provide
    def get_archive_course_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> ArchiveCourseUseCase:
        return ArchiveCourseUseCase(uow=uow)

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
    def get_create_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateTaskUseCase:
        return CreateTaskUseCase(uow=uow)

    @provide
    def get_update_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateTaskUseCase:
        return UpdateTaskUseCase(uow=uow)

    @provide
    def get_remove_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveTaskUseCase:
        return RemoveTaskUseCase(uow=uow)

    @provide
    def get_create_code_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateCodeTaskUseCase:
        return CreateCodeTaskUseCase(uow=uow)

    @provide
    def get_update_code_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateCodeTaskUseCase:
        return UpdateCodeTaskUseCase(uow=uow)

    @provide
    def get_remove_code_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveCodeTaskUseCase:
        return RemoveCodeTaskUseCase(uow=uow)

    @provide
    def get_create_test_case_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> CreateTestCaseUseCase:
        return CreateTestCaseUseCase(uow=uow)

    @provide
    def get_update_test_case_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateTestCaseUseCase:
        return UpdateTestCaseUseCase(uow=uow)

    @provide
    def get_remove_test_case_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> RemoveTestCaseUseCase:
        return RemoveTestCaseUseCase(uow=uow)

    @provide
    def get_submit_task_answer_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> SubmitTaskAnswerUseCase:
        return SubmitTaskAnswerUseCase(uow=uow)

    @provide
    def get_submit_code_submission_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        submission_queue: SubmissionQueue,
    ) -> SubmitCodeSubmissionUseCase:
        return SubmitCodeSubmissionUseCase(
            uow=uow,
            submission_queue=submission_queue,
        )

    @provide
    def get_get_code_submission_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetCodeSubmissionUseCase:
        return GetCodeSubmissionUseCase(uow=uow)

    @provide
    def get_list_code_submissions_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> ListCodeSubmissionsUseCase:
        return ListCodeSubmissionsUseCase(uow=uow)

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
    def get_start_question_attempt_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> StartQuestionAttemptUseCase:
        return StartQuestionAttemptUseCase(uow=uow)

    @provide
    def get_submit_question_answer_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> SubmitQuestionAnswerUseCase:
        return SubmitQuestionAnswerUseCase(uow=uow)

    @provide
    def get_get_question_attempt_result_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetQuestionAttemptResultUseCase:
        return GetQuestionAttemptResultUseCase(uow=uow)

    @provide
    def provide_get_lecture_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        access_service: CourseContentAccessService,
    ) -> GetLectureUseCase:
        return GetLectureUseCase(
            lecture_repository=uow.lectures,
            access_service=access_service,
        )

    @provide
    def get_get_question_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        access_service: CourseContentAccessService,
    ) -> GetQuestionUseCase:
        return GetQuestionUseCase(
            question_repository=uow.questions,
            answer_option_repository=uow.answer_options,
            access_service=access_service,
        )

    @provide
    def get_get_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        access_service: CourseContentAccessService,
    ) -> GetTaskUseCase:
        return GetTaskUseCase(
            task_repository=uow.tasks,
            access_service=access_service,
        )

    @provide
    def get_get_code_task_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
        access_service: CourseContentAccessService,
    ) -> GetCodeTaskUseCase:
        return GetCodeTaskUseCase(
            code_task_repository=uow.code_tasks,
            access_service=access_service,
        )

    @provide
    def get_get_my_profile_use_case(self) -> GetMyProfileUseCase:
        return GetMyProfileUseCase()

    @provide
    def get_get_my_course_analytics_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> GetMyCourseAnalyticsUseCase:
        return GetMyCourseAnalyticsUseCase(uow=uow)

    @provide
    def get_update_my_profile_use_case(
        self,
        uow: SqlAlchemyUnitOfWork,
    ) -> UpdateMyProfileUseCase:
        return UpdateMyProfileUseCase(uow=uow)

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
            raise AuthenticationError("Authentication credentials were not provided")

        try:
            user_id = token_service.get_user_id(credentials.credentials)
        except InvalidTokenError as exc:
            raise AuthenticationError("Token is invalid or expired") from exc

        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise AuthenticationError("Authenticated user was not found")

        return AuthenticatedUser(user)

    @provide
    async def get_current_user_or_none(
        self,
        credentials: HTTPAuthorizationCredentials | None,
        uow: SqlAlchemyUnitOfWork,
        token_service: TokenService,
    ) -> User | None:
        if credentials is None:
            return None

        if credentials.scheme.lower() != "bearer":
            raise AuthenticationError("Authentication scheme must be Bearer.")

        try:
            user_id = token_service.get_user_id(credentials.credentials)
        except InvalidTokenError as exc:
            raise AuthenticationError(str(exc)) from exc

        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise AuthenticationError("User from token was not found.")

        return user

    @provide
    def get_current_admin(
        self,
        current_user: AuthenticatedUser,
    ) -> AuthenticatedAdmin:
        if not current_user.can_manage_platform():
            raise PermissionDeniedError("Admin access is required.")

        return AuthenticatedAdmin(current_user)

    @provide
    def get_current_author_or_admin(self, current_user: AuthenticatedUser) -> User:
        if not current_user.can_manage_content():
            raise PermissionDeniedError("Author or admin access is required.")
        return current_user
