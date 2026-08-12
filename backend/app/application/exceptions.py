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


class AnswerOptionNotFoundError(ApplicationError):
    pass


class QuestionAlreadyUsedError(ApplicationError):
    pass


class QuestionAttemptNotFoundError(ApplicationError):
    pass