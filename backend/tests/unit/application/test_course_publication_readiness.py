from uuid import uuid4

import pytest

from app.application.services.course_publication_readiness_service import (
    CoursePublicationReadinessService,
)
from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.code_task import CodeTask, CodeTaskLanguage
from app.domain.entities.course import Course
from app.domain.entities.lecture import Lecture
from app.domain.entities.module import Module
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.section import Section


class DictRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, entity_id):
        return self.items.get(entity_id)

    async def get_by_ids(self, entity_ids):
        return [
            self.items[entity_id] for entity_id in entity_ids if entity_id in self.items
        ]

    async def add(self, entity):
        self.items[entity.id] = entity


class FakeTestCaseRepository:
    def __init__(self) -> None:
        self.items = {}

    async def add(self, entity):
        self.items[entity.id] = entity

    async def list_by_code_task_id(self, code_task_id):
        return [
            item for item in self.items.values() if item.code_task_id == code_task_id
        ]


class FakePublicationUnitOfWork:
    def __init__(self) -> None:
        self.modules = DictRepository()
        self.sections = DictRepository()
        self.lectures = DictRepository()
        self.questions = DictRepository()
        self.answer_options = DictRepository()
        self.code_tasks = DictRepository()
        self.test_cases = FakeTestCaseRepository()


def build_course() -> Course:
    return Course(
        id=uuid4(),
        author_id=uuid4(),
        title="FastAPI course",
        description="Clean architecture in practice.",
    )


@pytest.mark.asyncio
async def test_readiness_reports_missing_modules() -> None:
    uow = FakePublicationUnitOfWork()
    service = CoursePublicationReadinessService(uow)
    course = build_course()

    readiness = await service.inspect_course(course)

    assert readiness.is_ready is False
    assert readiness.issues[0].code == "course_without_modules"


@pytest.mark.asyncio
async def test_readiness_reports_question_and_code_task_problems() -> None:
    uow = FakePublicationUnitOfWork()
    service = CoursePublicationReadinessService(uow)
    course = build_course()

    module = Module(
        id=uuid4(),
        course_id=course.id,
        title="Module 1",
        description="Description",
        position=1,
    )
    section = Section(
        id=uuid4(),
        module_id=module.id,
        title="Section 1",
        description="Description",
        position=1,
    )
    lecture = Lecture(
        id=uuid4(),
        section_id=section.id,
        title="Lecture 1",
        content="Lecture content",
        position=1,
    )
    question = Question(
        id=uuid4(),
        section_id=section.id,
        text="Choose the correct option.",
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
        max_attempts=2,
        reward_points=5,
    )
    option = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text="Only option",
        position=1,
        is_correct=True,
    )
    code_task = CodeTask(
        id=uuid4(),
        section_id=section.id,
        title="Code task",
        statement="Solve it.",
        position=2,
        language=CodeTaskLanguage.PYTHON,
        starter_code="print(1)",
        max_attempts=2,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )

    course.add_module(module.id)
    module.add_section(section.id)
    section.add_lecture(lecture.id)
    section.add_question(question.id)
    question.add_answer_option(option.id)
    section.add_code_task(code_task.id)

    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.lectures.add(lecture)
    await uow.questions.add(question)
    await uow.answer_options.add(option)
    await uow.code_tasks.add(code_task)

    readiness = await service.inspect_course(course)

    codes = {str(issue.code) for issue in readiness.issues}
    assert readiness.is_ready is False
    assert "question_with_invalid_options" in codes
    assert "code_task_without_test_cases" in codes
