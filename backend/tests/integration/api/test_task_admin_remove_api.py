from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.infrastructure.database import models
from app.infrastructure.database.models import (
    CodeSubmissionModel,
    CodeTaskModel,
    TaskAttemptModel,
    TaskModel,
)

TASK_PAYLOAD = {
    "title": "Disposable task",
    "statement": "Enter the HTTP method used for reading a resource.",
    "position": 1,
    "check_type": "exact_match",
    "expected_answer": "GET",
    "max_attempts": 1,
    "reward_points": 1,
}

CODE_TASK_PAYLOAD = {
    "title": "Disposable code task",
    "statement": "Read two integers and print their sum.",
    "position": 1,
    "language": "python",
    "starter_code": "print(1)",
    "max_attempts": 1,
    "reward_points": 1,
    "time_limit_seconds": 2,
    "memory_limit_mb": 128,
}


def build_test_case_payload(position: int) -> dict:
    return {
        "position": position,
        "input_data": f"{position} {position}",
        "expected_output": str(position + position),
        "is_hidden": False,
        "explanation": "",
    }


async def create_task(client, headers, section_id: str) -> dict:
    response = await client.post(
        f"/api/admin/sections/{section_id}/tasks",
        headers=headers,
        json=TASK_PAYLOAD,
    )
    assert response.status_code == 201
    return response.json()


async def create_code_task(client, headers, section_id: str) -> dict:
    response = await client.post(
        f"/api/admin/sections/{section_id}/code-tasks",
        headers=headers,
        json=CODE_TASK_PAYLOAD,
    )
    assert response.status_code == 201
    return response.json()


async def create_test_case(client, headers, code_task_id: str, position: int) -> dict:
    response = await client.post(
        f"/api/admin/code-tasks/{code_task_id}/test-cases",
        headers=headers,
        json=build_test_case_payload(position),
    )
    assert response.status_code == 201
    return response.json()


async def fetch_section_structure(client, course_id: str) -> dict:
    response = await client.get(f"/api/courses/{course_id}/structure")
    assert response.status_code == 200
    return response.json()["modules"][0]["sections"][0]


@pytest.mark.asyncio
async def test_remove_task_returns_204_and_detaches_from_section(
    client,
    admin_auth_headers,
    seeded_course_tree,
) -> None:
    task = await create_task(client, admin_auth_headers, seeded_course_tree.section_id)

    section = await fetch_section_structure(client, seeded_course_tree.course_id)
    assert task["id"] in section["task_ids"]

    response = await client.delete(
        f"/api/admin/tasks/{task['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    section = await fetch_section_structure(client, seeded_course_tree.course_id)
    assert section["task_ids"] == []
    assert section["tasks"] == []

    read_response = await client.get(f"/api/tasks/{task['id']}")
    assert read_response.status_code == 404
    assert read_response.json()["error"] == "task_not_found"


@pytest.mark.asyncio
async def test_remove_code_task_returns_204_and_detaches_from_section(
    client,
    admin_auth_headers,
    seeded_course_tree,
) -> None:
    code_task = await create_code_task(
        client, admin_auth_headers, seeded_course_tree.section_id
    )

    section = await fetch_section_structure(client, seeded_course_tree.course_id)
    assert code_task["id"] in section["code_task_ids"]

    response = await client.delete(
        f"/api/admin/code-tasks/{code_task['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    section = await fetch_section_structure(client, seeded_course_tree.course_id)
    assert section["code_task_ids"] == []
    assert section["code_tasks"] == []

    read_response = await client.get(f"/api/code-tasks/{code_task['id']}")
    assert read_response.status_code == 404
    assert read_response.json()["error"] == "code_task_not_found"


@pytest.mark.asyncio
async def test_remove_test_case_returns_204_and_keeps_code_task_consistent(
    client,
    admin_auth_headers,
    seeded_course_tree,
    session_factory,
) -> None:
    code_task = await create_code_task(
        client, admin_auth_headers, seeded_course_tree.section_id
    )
    first_case = await create_test_case(
        client, admin_auth_headers, code_task["id"], position=1
    )
    second_case = await create_test_case(
        client, admin_auth_headers, code_task["id"], position=2
    )

    response = await client.delete(
        f"/api/admin/test-cases/{first_case['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    async with session_factory() as session:
        assert await session.get(models.TestCaseModel, first_case["id"]) is None
        assert await session.get(models.TestCaseModel, second_case["id"]) is not None
        assert await session.get(CodeTaskModel, code_task["id"]) is not None

    read_response = await client.get(f"/api/code-tasks/{code_task['id']}")
    assert read_response.status_code == 200


@pytest.mark.asyncio
async def test_remove_task_with_attempts_is_rejected(
    client,
    admin_auth_headers,
    seeded_course_tree,
    seeded_student_user,
    session_factory,
) -> None:
    task = await create_task(client, admin_auth_headers, seeded_course_tree.section_id)

    async with session_factory() as session:
        session.add(
            TaskAttemptModel(
                id=str(uuid4()),
                task_id=task["id"],
                student_id=seeded_student_user.id,
                submitted_answer="GET",
                attempt_number=1,
                status="correct",
                awarded_points=1,
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/tasks/{task['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "application_error"

    async with session_factory() as session:
        assert await session.get(TaskModel, task["id"]) is not None


@pytest.mark.asyncio
async def test_remove_code_task_with_submission_is_rejected(
    client,
    admin_auth_headers,
    seeded_course_tree,
    seeded_student_user,
    session_factory,
) -> None:
    code_task = await create_code_task(
        client, admin_auth_headers, seeded_course_tree.section_id
    )

    async with session_factory() as session:
        session.add(
            CodeSubmissionModel(
                id=str(uuid4()),
                code_task_id=code_task["id"],
                student_id=seeded_student_user.id,
                source_code="print(1)",
                attempt_number=1,
                status="pending",
                created_at=datetime.now(UTC),
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/code-tasks/{code_task['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "application_error"

    async with session_factory() as session:
        assert await session.get(CodeTaskModel, code_task["id"]) is not None


@pytest.mark.asyncio
async def test_remove_test_case_when_code_task_has_submission_is_rejected(
    client,
    admin_auth_headers,
    seeded_course_tree,
    seeded_student_user,
    session_factory,
) -> None:
    code_task = await create_code_task(
        client, admin_auth_headers, seeded_course_tree.section_id
    )
    first_case = await create_test_case(
        client, admin_auth_headers, code_task["id"], position=1
    )
    second_case = await create_test_case(
        client, admin_auth_headers, code_task["id"], position=2
    )

    async with session_factory() as session:
        session.add(
            CodeSubmissionModel(
                id=str(uuid4()),
                code_task_id=code_task["id"],
                student_id=seeded_student_user.id,
                source_code="print(1)",
                attempt_number=1,
                status="pending",
                created_at=datetime.now(UTC),
            )
        )
        await session.commit()

    response = await client.delete(
        f"/api/admin/test-cases/{first_case['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "application_error"

    async with session_factory() as session:
        assert await session.get(models.TestCaseModel, first_case["id"]) is not None
        assert await session.get(models.TestCaseModel, second_case["id"]) is not None


@pytest.mark.asyncio
async def test_remove_last_test_case_is_rejected(
    client,
    admin_auth_headers,
    seeded_course_tree,
    session_factory,
) -> None:
    code_task = await create_code_task(
        client, admin_auth_headers, seeded_course_tree.section_id
    )
    only_case = await create_test_case(
        client, admin_auth_headers, code_task["id"], position=1
    )

    response = await client.delete(
        f"/api/admin/test-cases/{only_case['id']}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "domain_error"

    async with session_factory() as session:
        assert await session.get(models.TestCaseModel, only_case["id"]) is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("resource", "error"),
    [
        ("tasks", "task_not_found"),
        ("code-tasks", "code_task_not_found"),
        ("test-cases", "test_case_not_found"),
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
@pytest.mark.parametrize("resource", ["tasks", "code-tasks", "test-cases"])
async def test_remove_requires_authentication(client, resource) -> None:
    response = await client.delete(f"/api/admin/{resource}/{uuid4()}")

    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"


@pytest.mark.asyncio
@pytest.mark.parametrize("resource", ["tasks", "code-tasks", "test-cases"])
async def test_remove_requires_author_or_admin(
    client,
    student_auth_headers,
    resource,
) -> None:
    response = await client.delete(
        f"/api/admin/{resource}/{uuid4()}",
        headers=student_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_remove_task_of_other_author_course_is_forbidden(
    client,
    other_author_auth_headers,
    seeded_course_tree,
    admin_auth_headers,
) -> None:
    task = await create_task(client, admin_auth_headers, seeded_course_tree.section_id)

    response = await client.delete(
        f"/api/admin/tasks/{task['id']}",
        headers=other_author_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"
