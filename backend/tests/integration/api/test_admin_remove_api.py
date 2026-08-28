from uuid import uuid4

import pytest

from app.infrastructure.database.models import (
    CourseModel,
    LectureModel,
    ModuleModel,
    SectionModel,
)


@pytest.mark.asyncio
async def test_remove_course_returns_204_and_removes_content_tree(
    client,
    admin_auth_headers,
    seeded_course_tree,
    session_factory,
) -> None:
    control_course_id = str(uuid4())
    async with session_factory() as session:
        session.add(
            CourseModel(
                id=control_course_id,
                author_id=seeded_course_tree.author_id,
                title="Control course",
                description="Must survive removal of another course.",
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    async with session_factory() as session:
        assert await session.get(CourseModel, seeded_course_tree.course_id) is None
        assert await session.get(ModuleModel, seeded_course_tree.module_id) is None
        assert await session.get(SectionModel, seeded_course_tree.section_id) is None
        assert await session.get(LectureModel, seeded_course_tree.lecture_id) is None
        assert await session.get(CourseModel, control_course_id) is not None


@pytest.mark.asyncio
async def test_remove_module_returns_204_and_preserves_course(
    client,
    admin_auth_headers,
    seeded_course_tree,
    session_factory,
) -> None:
    control_module_id = str(uuid4())
    async with session_factory() as session:
        session.add(
            ModuleModel(
                id=control_module_id,
                course_id=seeded_course_tree.course_id,
                title="Control module",
                description="Must survive removal of its sibling.",
                position=2,
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/modules/{seeded_course_tree.module_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    async with session_factory() as session:
        assert await session.get(CourseModel, seeded_course_tree.course_id) is not None
        assert await session.get(ModuleModel, seeded_course_tree.module_id) is None
        assert await session.get(SectionModel, seeded_course_tree.section_id) is None
        assert await session.get(LectureModel, seeded_course_tree.lecture_id) is None
        assert await session.get(ModuleModel, control_module_id) is not None


@pytest.mark.asyncio
async def test_remove_section_returns_204_and_preserves_parents(
    client,
    admin_auth_headers,
    seeded_course_tree,
    session_factory,
) -> None:
    control_section_id = str(uuid4())
    async with session_factory() as session:
        session.add(
            SectionModel(
                id=control_section_id,
                module_id=seeded_course_tree.module_id,
                title="Control section",
                description="Must survive removal of its sibling.",
                position=2,
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/sections/{seeded_course_tree.section_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    async with session_factory() as session:
        assert await session.get(CourseModel, seeded_course_tree.course_id) is not None
        assert await session.get(ModuleModel, seeded_course_tree.module_id) is not None
        assert await session.get(SectionModel, seeded_course_tree.section_id) is None
        assert await session.get(LectureModel, seeded_course_tree.lecture_id) is None
        assert await session.get(SectionModel, control_section_id) is not None


@pytest.mark.asyncio
async def test_remove_lecture_returns_204_and_preserves_parents(
    client,
    admin_auth_headers,
    seeded_course_tree,
    session_factory,
) -> None:
    control_lecture_id = str(uuid4())
    async with session_factory() as session:
        session.add(
            LectureModel(
                id=control_lecture_id,
                section_id=seeded_course_tree.section_id,
                title="Control lecture",
                content="Must survive removal of its sibling.",
                position=2,
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/lectures/{seeded_course_tree.lecture_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    async with session_factory() as session:
        assert await session.get(CourseModel, seeded_course_tree.course_id) is not None
        assert await session.get(ModuleModel, seeded_course_tree.module_id) is not None
        assert await session.get(SectionModel, seeded_course_tree.section_id) is not None
        assert await session.get(LectureModel, seeded_course_tree.lecture_id) is None
        assert await session.get(LectureModel, control_lecture_id) is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("resource", "error"),
    [
        ("courses", "course_not_found"),
        ("modules", "module_not_found"),
        ("sections", "section_not_found"),
        ("lectures", "lecture_not_found"),
    ],
)
async def test_remove_missing_resource_returns_404(
    client,
    admin_auth_headers,
    resource,
    error,
) -> None:
    response = await client.delete(
        f"/api/admin/{resource}/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "resource",
    ["courses", "modules", "sections", "lectures"],
)
async def test_remove_requires_authentication(client, resource) -> None:
    response = await client.delete(f"/api/admin/{resource}/{uuid4()}")

    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "resource",
    ["courses", "modules", "sections", "lectures"],
)
async def test_remove_requires_admin(client, student_auth_headers, resource) -> None:
    response = await client.delete(
        f"/api/admin/{resource}/{uuid4()}",
        headers=student_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"
