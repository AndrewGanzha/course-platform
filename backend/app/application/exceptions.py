from app.application.dto.course_publication import CoursePublicationReadinessDTO


class ApplicationError(Exception):
    """Base exception for application-layer errors."""


class CourseNotFoundError(ApplicationError):
    pass


class LectureNotFoundError(ApplicationError):
    pass


class ModuleNotFoundError(ApplicationError):
    pass


class SectionNotFoundError(ApplicationError):
    pass


class UserAlreadyExistsError(ApplicationError):
    pass


class InvalidCredentialsError(ApplicationError):
    pass


class QuestionNotFoundError(ApplicationError):
    pass


class PermissionDeniedError(ApplicationError):
    pass


class InvalidCoverImageError(ApplicationError):
    pass


class AnswerOptionNotFoundError(ApplicationError):
    pass


class QuestionAlreadyUsedError(ApplicationError):
    pass


class QuestionAttemptNotFoundError(ApplicationError):
    pass


class InvalidProgressError(ApplicationError):
    pass


class TaskNotFoundError(ApplicationError):
    pass


class TaskAlreadyUsedError(ApplicationError):
    pass


class CodeTaskAlreadyUsedError(ApplicationError):
    pass


class TestCaseNotFoundError(ApplicationError):
    pass


class CodeTaskNotFoundError(ApplicationError):
    pass


class CodeSubmissionNotFoundError(ApplicationError):
    pass


class RetryableExecutionError(ApplicationError):
    pass


class CoursePublicationNotReadyError(ApplicationError):
    def __init__(self, readiness: CoursePublicationReadinessDTO) -> None:
        super().__init__("Course is not ready for publication.")
        self.readiness = readiness


class LectureCommentNotFoundError(ApplicationError):
    pass
