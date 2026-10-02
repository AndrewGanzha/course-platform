from abc import ABC, abstractmethod

from app.application.interfaces.repositories import (
    AnswerOptionRepository,
    CodeSubmissionRepository,
    CodeTaskRepository,
    CourseRepository,
    CourseReviewRepository,
    LectureCommentRepository,
    LectureRepository,
    ModuleRepository,
    ProgressRepository,
    QuestionAttemptRepository,
    QuestionRepository,
    SectionRepository,
    TaskAttemptRepository,
    TaskRepository,
    TestCaseRepository,
    UserRepository,
)


class UnitOfWork(ABC):
    courses: CourseRepository
    modules: ModuleRepository
    sections: SectionRepository
    lectures: LectureRepository
    users: UserRepository
    questions: QuestionRepository
    answer_options: AnswerOptionRepository
    question_attempts: QuestionAttemptRepository
    tasks: TaskRepository
    task_attempts: TaskAttemptRepository
    progress: ProgressRepository
    code_tasks: CodeTaskRepository
    test_cases: TestCaseRepository
    code_submissions: CodeSubmissionRepository
    course_reviews: CourseReviewRepository
    lecture_comments: LectureCommentRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
