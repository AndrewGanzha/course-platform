from uuid import UUID, uuid4

import pytest

from app.infrastructure.database.models import (
    CourseModel,
    LectureModel,
    ModuleModel,
    SectionModel,
)
from app.infrastructure.database.repositories.course_repository import (
    SqlAlchemyCourseRepository,
)
from app.infrastructure.database.repositories.lecture_repository import (
    SqlAlchemyLectureRepository,
)
from app.infrastructure.database.repositories.module_repository import (
    SqlAlchemyModuleRepository,
)
from app.infrastructure.database.repositories.section_repository import (
    SqlAlchemySectionRepository,
)


REPOSITORIES = (
    SqlAlchemyCourseRepository,
    SqlAlchemyModuleRepository,
    SqlAlchemySectionRepository,
    SqlAlchemyLectureRepository,
)


def build_control_model(model_type, seeded_course_tree, control_id):
    if model_type is CourseModel:
        return CourseModel(
            id=control_id,
            author_id=seeded_course_tree.author_id,
            title="Control course",
            description="Must survive removal of another course.",
        )
    if model_type is ModuleModel:
        return ModuleModel(
            id=control_id,
            course_id=seeded_course_tree.course_id,
            title="Control module",
            description="Must survive removal of its sibling.",
            position=2,
        )
    if model_type is SectionModel:
        return SectionModel(
            id=control_id,
            module_id=seeded_course_tree.module_id,
            title="Control section",
            description="Must survive removal of its sibling.",
            position=2,
        )
    return LectureModel(
        id=control_id,
        section_id=seeded_course_tree.section_id,
        title="Control lecture",
        content="Must survive removal of its sibling.",
        position=2,
    )


async def assert_tree_presence(session_factory, seeded_course_tree, expected) -> None:
    async with session_factory() as session:
        actual = (
            await session.get(CourseModel, seeded_course_tree.course_id) is not None,
            await session.get(ModuleModel, seeded_course_tree.module_id) is not None,
            await session.get(SectionModel, seeded_course_tree.section_id) is not None,
            await session.get(LectureModel, seeded_course_tree.lecture_id) is not None,
        )

    assert actual == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("repository_type", REPOSITORIES)
async def test_remove_missing_id_is_no_op(
    repository_type,
    session_factory,
    seeded_course_tree,
) -> None:
    async with session_factory() as session:
        repository = repository_type(session)
        await repository.remove(uuid4())
        await session.commit()

    await assert_tree_presence(
        session_factory,
        seeded_course_tree,
        expected=(True, True, True, True),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("repository_type", "id_attribute", "control_model_type", "expected"),
    (
        (
            SqlAlchemyCourseRepository,
            "course_id",
            CourseModel,
            (False, False, False, False),
        ),
        (
            SqlAlchemyModuleRepository,
            "module_id",
            ModuleModel,
            (True, False, False, False),
        ),
        (
            SqlAlchemySectionRepository,
            "section_id",
            SectionModel,
            (True, True, False, False),
        ),
        (
            SqlAlchemyLectureRepository,
            "lecture_id",
            LectureModel,
            (True, True, True, False),
        ),
    ),
)
async def test_remove_deletes_requested_row_and_only_its_descendants(
    repository_type,
    id_attribute,
    control_model_type,
    expected,
    session_factory,
    seeded_course_tree,
) -> None:
    resource_id = UUID(getattr(seeded_course_tree, id_attribute))
    control_id = str(uuid4())

    async with session_factory() as session:
        session.add(
            build_control_model(
                control_model_type,
                seeded_course_tree,
                control_id,
            )
        )
        await session.flush()

        repository = repository_type(session)
        await repository.remove(resource_id)
        await session.commit()

    await assert_tree_presence(session_factory, seeded_course_tree, expected)

    async with session_factory() as session:
        assert await session.get(control_model_type, control_id) is not None
