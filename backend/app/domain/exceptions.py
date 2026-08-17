class DomainError(Exception):
    """Base exception for domain-layer violations."""


class InvalidCourseError(DomainError):
    pass


class InvalidModuleError(DomainError):
    pass


class InvalidSectionError(DomainError):
    pass


class InvalidLectureError(DomainError):
    pass


class InvalidUserError(DomainError):
    pass


class SectionQuestionAlreadyAttachedError(DomainError):
    pass


class SectionQuestionNotAttachedError(DomainError):
    pass


class InvalidQuestionError(DomainError):
    pass


class InvalidAnswerOptionError(DomainError):
    pass


class InvalidQuestionAttemptError(DomainError):
    pass


class QuestionAttemptLimitExceededError(DomainError):
    pass


class InvalidQuestionResultError(DomainError):
    pass


class QuestionAlreadySolvedError(DomainError):
    pass


class InvalidProgressError(DomainError):
    pass