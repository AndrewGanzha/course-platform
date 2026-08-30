from uuid import uuid4

import pytest

from app.application.exceptions import QuestionAlreadyUsedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.use_cases.answer_options.remove_answer_option import (
    RemoveAnswerOptionCommand,
    RemoveAnswerOptionUseCase,
)
from app.application.use_cases.questions.remove_question import (
    RemoveQuestionCommand,
    RemoveQuestionUseCase,
)
from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.course import Course
from app.domain.entities.module import Module
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.section import Section
from app.domain.entities.user import User, UserRole
from app.domain.exceptions import InvalidQuestionError


class FakeRepository:
    def __init__(self) -> None:
        self.items = {}
        self.updated_ids = []
        self.removed_ids = []

    async def get_by_id(self, entity_id):
        return self.items.get(entity_id)

    async def get_by_ids(self, entity_ids):
        return [self.items[entity_id] for entity_id in entity_ids]

    async def add(self, entity) -> None:
        self.items[entity.id] = entity

    async def update(self, entity) -> None:
        self.updated_ids.append(entity.id)
        self.items[entity.id] = entity

    async def remove(self, entity_id) -> None:
        self.removed_ids.append(entity_id)
        self.items.pop(entity_id, None)


class FakeQuestionAttemptRepository:
    def __init__(self) -> None:
        self.used_question_ids = set()

    async def exists_by_question_id(self, question_id) -> bool:
        return question_id in self.used_question_ids


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.courses = FakeRepository()
        self.modules = FakeRepository()
        self.sections = FakeRepository()
        self.lectures = FakeRepository()
        self.questions = FakeRepository()
        self.answer_options = FakeRepository()
        self.question_attempts = FakeQuestionAttemptRepository()
        self.users = FakeRepository()
        self.progress = FakeRepository()
        self.commit_count = 0
        self.rollback_count = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


def make_author() -> User:
    return User(
        id=uuid4(),
        email='author@example.com',
        hashed_password='hashed-password',
        role=UserRole.AUTHOR,
    )


async def seed_question_tree(
    uow: FakeUnitOfWork,
    actor: User,
    question_type: QuestionType = QuestionType.SINGLE_CHOICE,
    option_correctness: tuple[bool, ...] = (False, False, True),
):
    course = Course(
        id=uuid4(),
        author_id=actor.id,
        title='Course',
        description='Description',
    )
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title='Module',
        description='Description',
        position=1,
    )
    section = Section(
        id=uuid4(),
        module_id=module.id,
        title='Section',
        position=1,
    )
    question = Question(
        id=uuid4(),
        section_id=section.id,
        text='Question?',
        position=1,
        question_type=question_type,
    )
    options = [
        AnswerOption(
            id=uuid4(),
            question_id=question.id,
            text=f'Option {position}',
            position=position,
            is_correct=is_correct,
        )
        for position, is_correct in enumerate(option_correctness, start=1)
    ]

    course.add_module(module.id)
    module.add_section(section.id)
    section.add_question(question.id)
    for option in options:
        question.add_answer_option(option.id)

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.questions.add(question)
    for option in options:
        await uow.answer_options.add(option)

    return section, question, options


@pytest.mark.asyncio
async def test_remove_question_detaches_and_deletes_unused_question() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    section, question, _ = await seed_question_tree(uow, actor)

    use_case = RemoveQuestionUseCase(uow=uow)
    await use_case.execute(
        RemoveQuestionCommand(actor=actor, question_id=question.id)
    )

    assert question.id not in section.question_ids
    assert question.id not in uow.questions.items
    assert uow.sections.updated_ids == [section.id]
    assert uow.questions.removed_ids == [question.id]
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_remove_question_rejects_question_with_attempts() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    section, question, _ = await seed_question_tree(uow, actor)
    uow.question_attempts.used_question_ids.add(question.id)

    use_case = RemoveQuestionUseCase(uow=uow)
    with pytest.raises(QuestionAlreadyUsedError):
        await use_case.execute(
            RemoveQuestionCommand(actor=actor, question_id=question.id)
        )

    assert question.id in section.question_ids
    assert question.id in uow.questions.items
    assert uow.questions.removed_ids == []
    assert uow.commit_count == 0
    assert uow.rollback_count == 1


@pytest.mark.asyncio
async def test_remove_answer_option_deletes_option_when_question_stays_valid() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    _, question, options = await seed_question_tree(uow, actor)
    option_to_remove = options[0]

    use_case = RemoveAnswerOptionUseCase(uow=uow)
    await use_case.execute(
        RemoveAnswerOptionCommand(
            actor=actor,
            answer_option_id=option_to_remove.id,
        )
    )

    assert option_to_remove.id not in question.answer_option_ids
    assert option_to_remove.id not in uow.answer_options.items
    assert uow.questions.updated_ids == [question.id]
    assert uow.answer_options.removed_ids == [option_to_remove.id]
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_remove_answer_option_rejects_question_with_attempts() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    _, question, options = await seed_question_tree(uow, actor)
    option_to_remove = options[0]
    uow.question_attempts.used_question_ids.add(question.id)

    use_case = RemoveAnswerOptionUseCase(uow=uow)
    with pytest.raises(QuestionAlreadyUsedError):
        await use_case.execute(
            RemoveAnswerOptionCommand(
                actor=actor,
                answer_option_id=option_to_remove.id,
            )
        )

    assert option_to_remove.id in question.answer_option_ids
    assert option_to_remove.id in uow.answer_options.items
    assert uow.answer_options.removed_ids == []
    assert uow.commit_count == 0
    assert uow.rollback_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        'question_type',
        'option_correctness',
        'remove_index',
        'error_message',
    ),
    [
        (
            QuestionType.SINGLE_CHOICE,
            (False, True),
            0,
            'at least two answer options',
        ),
        (
            QuestionType.SINGLE_CHOICE,
            (True, False, False),
            0,
            'at least one correct answer option',
        ),
        (
            QuestionType.SINGLE_CHOICE,
            (True, True, False),
            2,
            'exactly one correct answer option',
        ),
        (
            QuestionType.MULTIPLE_CHOICE,
            (True, True, False),
            0,
            'at least two correct answer options',
        ),
    ],
)
async def test_remove_answer_option_rejects_invalid_remaining_configuration(
    question_type,
    option_correctness,
    remove_index,
    error_message,
) -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    _, _, options = await seed_question_tree(
        uow,
        actor,
        question_type=question_type,
        option_correctness=option_correctness,
    )
    option_to_remove = options[remove_index]

    use_case = RemoveAnswerOptionUseCase(uow=uow)
    with pytest.raises(InvalidQuestionError, match=error_message):
        await use_case.execute(
            RemoveAnswerOptionCommand(
                actor=actor,
                answer_option_id=option_to_remove.id,
            )
        )

    assert option_to_remove.id in uow.answer_options.items
    assert uow.answer_options.removed_ids == []
    assert uow.commit_count == 0
    assert uow.rollback_count == 1
