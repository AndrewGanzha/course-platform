from app.presentation.api.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisteredUserResponse,
    RegisterUserRequest,
    TokenResponse,
)
from app.presentation.api.schemas.author_course_analytics import (
    AuthorCourseAnalyticsResponse,
    AuthorModuleAnalyticsResponse,
    DifficultQuestionAnalyticsResponse,
    DifficultTaskAnalyticsResponse,
    ProblematicCodeTaskAnalyticsResponse,
)
from app.presentation.api.schemas.catalog import (
    CourseCatalogCardResponse,
    CourseCatalogCountersResponse,
    CourseCatalogItemResponse,
    CourseCatalogModulePreviewResponse,
    CourseCatalogSectionPreviewResponse,
    CourseRatingSummaryResponse,
)
from app.presentation.api.schemas.code_submissions import (
    CodeSubmissionResponse,
    SubmitCodeSubmissionRequest,
)
from app.presentation.api.schemas.code_tasks import (
    CodeTaskResponse,
    CreateCodeTaskRequest,
    UpdateCodeTaskRequest,
)
from app.presentation.api.schemas.content import (
    AnswerOptionDetailsResponse,
    CodeTaskDetailsResponse,
    CodeTaskStructureResponse,
    CourseListItemResponse,
    CoursePublicationErrorResponse,
    CoursePublicationIssueResponse,
    CoursePublicationReadinessResponse,
    CourseResponse,
    CourseStructureResponse,
    LectureResponse,
    LectureStructureResponse,
    ModuleStructureResponse,
    QuestionDetailsResponse,
    SectionStructureResponse,
    TaskDetailsResponse,
    TaskStructureResponse,
)
from app.presentation.api.schemas.course_reviews import (
    CourseReviewResponse,
    UpsertCourseReviewRequest,
)
from app.presentation.api.schemas.courses import (
    CreateCourseRequest,
    UpdateCourseRequest,
)
from app.presentation.api.schemas.errors import ErrorResponse
from app.presentation.api.schemas.lectures import (
    CreateLectureRequest,
    UpdateLectureRequest,
)
from app.presentation.api.schemas.modules import (
    CreateModuleRequest,
    ModuleResponse,
    UpdateModuleRequest,
)
from app.presentation.api.schemas.profile import (
    UpdateMyProfileRequest,
    UserProfileResponse,
)
from app.presentation.api.schemas.question_attempts import (
    QuestionAttemptResultResponse,
    StartQuestionAttemptResponse,
    SubmitQuestionAnswerRequest,
)
from app.presentation.api.schemas.questions import (
    AnswerOptionResponse,
    CreateAnswerOptionRequest,
    CreateQuestionRequest,
    QuestionResponse,
    UpdateAnswerOptionRequest,
    UpdateQuestionRequest,
)
from app.presentation.api.schemas.sections import (
    CreateSectionRequest,
    SectionResponse,
    UpdateSectionRequest,
)
from app.presentation.api.schemas.student_analytics import (
    StudentCourseAnalyticsResponse,
    StudentModuleAnalyticsResponse,
    StudentWeakCodeTaskResponse,
    StudentWeakQuestionResponse,
    StudentWeakTaskResponse,
)
from app.presentation.api.schemas.task_attempts import (
    SubmitTaskAnswerRequest,
    TaskAttemptResponse,
)
from app.presentation.api.schemas.tasks import (
    CreateTaskRequest,
    TaskResponse,
    UpdateTaskRequest,
)
from app.presentation.api.schemas.test_cases import (
    CreateTestCaseRequest,
    TestCaseResponse,
    UpdateTestCaseRequest,
)

__all__ = [
    "AnswerOptionDetailsResponse",
    "CodeTaskDetailsResponse",
    "CodeTaskStructureResponse",
    "CourseCatalogCardResponse",
    "CourseCatalogCountersResponse",
    "CourseCatalogItemResponse",
    "CourseCatalogModulePreviewResponse",
    "CourseCatalogSectionPreviewResponse",
    "CourseRatingSummaryResponse",
    "CourseReviewResponse",
    "UpsertCourseReviewRequest",
    "CourseListItemResponse",
    "CourseResponse",
    "CoursePublicationIssueResponse",
    "CoursePublicationReadinessResponse",
    "CoursePublicationErrorResponse",
    "CourseStructureResponse",
    "LectureResponse",
    "LectureStructureResponse",
    "ModuleStructureResponse",
    "QuestionDetailsResponse",
    "SectionStructureResponse",
    "TaskDetailsResponse",
    "TaskStructureResponse",
    "CreateCourseRequest",
    "UpdateCourseRequest",
    "CreateModuleRequest",
    "UpdateModuleRequest",
    "ModuleResponse",
    "CreateSectionRequest",
    "UpdateSectionRequest",
    "SectionResponse",
    "CreateLectureRequest",
    "UpdateLectureRequest",
    "ErrorResponse",
    "RegisterUserRequest",
    "RegisteredUserResponse",
    "LoginRequest",
    "TokenResponse",
    "CurrentUserResponse",
    "CreateQuestionRequest",
    "UpdateQuestionRequest",
    "QuestionResponse",
    "CreateAnswerOptionRequest",
    "UpdateAnswerOptionRequest",
    "AnswerOptionResponse",
    "StartQuestionAttemptResponse",
    "SubmitQuestionAnswerRequest",
    "QuestionAttemptResultResponse",
    "CreateTaskRequest",
    "TaskResponse",
    "UpdateTaskRequest",
    "CodeTaskResponse",
    "CreateCodeTaskRequest",
    "UpdateCodeTaskRequest",
    "CreateTestCaseRequest",
    "TestCaseResponse",
    "UpdateTestCaseRequest",
    "SubmitTaskAnswerRequest",
    "TaskAttemptResponse",
    "CodeSubmissionResponse",
    "SubmitCodeSubmissionRequest",
    "UserProfileResponse",
    "UpdateMyProfileRequest",
    "StudentCourseAnalyticsResponse",
    "StudentModuleAnalyticsResponse",
    "StudentWeakQuestionResponse",
    "StudentWeakTaskResponse",
    "StudentWeakCodeTaskResponse",
    "AuthorCourseAnalyticsResponse",
    "AuthorModuleAnalyticsResponse",
    "DifficultQuestionAnalyticsResponse",
    "DifficultTaskAnalyticsResponse",
    "ProblematicCodeTaskAnalyticsResponse",
]
