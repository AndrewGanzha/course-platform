class DomainError(Exception):
    """Base exception for domain-layer violations."""


class InvalidCourseError(DomainError):
    pass