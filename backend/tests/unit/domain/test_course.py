from uuid import uuid4

import pytest

from app.domain.entities.course import Course
from app.domain.exceptions import InvalidCourseError


def test_course_is_created_with_valid_data() -> None:
    course = Course(
        id=uuid4(),
        title='FastAPI course',
        description='Clean architecture in practice.',
    )

    assert course.title == 'FastAPI course'
    assert course.description == 'Clean architecture in practice.'
    assert course.module_ids == []


def test_course_raises_error_when_title_is_blank() -> None:
    with pytest.raises(InvalidCourseError):
        Course(
            id=uuid4(),
            title='   ',
            description='Valid description',
        )


def test_course_raises_error_when_description_is_blank() -> None:
    with pytest.raises(InvalidCourseError):
        Course(
            id=uuid4(),
            title='Valid title',
            description='   ',
        )


def test_course_update_changes_state() -> None:
    course = Course(
        id=uuid4(),
        title='Old title',
        description='Old description',
    )

    course.update(title='New title', description='New description')

    assert course.title == 'New title'
    assert course.description == 'New description'


def test_course_remove_module_removes_module_id() -> None:
    module_id = uuid4()
    course = Course(
        id=uuid4(),
        title='FastAPI course',
        description='Clean architecture in practice.',
        module_ids=[module_id],
    )

    course.remove_module(module_id)

    assert module_id not in course.module_ids
