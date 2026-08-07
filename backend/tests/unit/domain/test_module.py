from uuid import uuid4

import pytest

from app.domain.entities.module import Module
from app.domain.exceptions import InvalidModuleError


def test_module_is_created_with_valid_data() -> None:
    module = Module(
        id=uuid4(),
        course_id=uuid4(),
        title='Module 1',
        description='Introduction module',
        position=1,
    )

    assert module.title == 'Module 1'
    assert module.position == 1
    assert module.section_ids == []


def test_module_raises_error_when_position_is_not_positive() -> None:
    with pytest.raises(InvalidModuleError):
        Module(
            id=uuid4(),
            course_id=uuid4(),
            title='Module 1',
            description='Introduction module',
            position=0,
        )


def test_module_update_changes_fields() -> None:
    module = Module(
        id=uuid4(),
        course_id=uuid4(),
        title='Old title',
        description='Old description',
        position=1,
    )

    module.update(title='New title', description='New description', position=2)

    assert module.title == 'New title'
    assert module.description == 'New description'
    assert module.position == 2


def test_module_remove_section_removes_section_id() -> None:
    section_id = uuid4()
    module = Module(
        id=uuid4(),
        course_id=uuid4(),
        title='Module 1',
        description='Introduction module',
        position=1,
        section_ids=[section_id],
    )

    module.remove_section(section_id)

    assert section_id not in module.section_ids
