import pytest

import app.presentation.api.dependencies as api_dependencies


class FakeSubmissionQueue:
    def __init__(self) -> None:
        self.items = []

    async def enqueue(self, submission_id) -> None:
        self.items.append(submission_id)


@pytest.fixture
def fake_submission_queue(monkeypatch):
    queue = FakeSubmissionQueue()
    monkeypatch.setattr(
        api_dependencies,
        "build_submission_queue",
        lambda: queue,
    )
    return queue


async def create_authoring_tree(client, headers) -> dict:
    course_response = await client.post(
        "/api/admin/courses",
        headers=headers,
        json={
            "title": "Authoring removal course",
            "description": "Course used by the removal lifecycle.",
        },
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    module_response = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=headers,
        json={"title": "Module", "description": "Module", "position": 1},
    )
    assert module_response.status_code == 201
    module_id = module_response.json()["id"]

    section_response = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=headers,
        json={"title": "Section", "description": "Section", "position": 1},
    )
    assert section_response.status_code == 201
    section_id = section_response.json()["id"]

    return {"course_id": course_id, "module_id": module_id, "section_id": section_id}


async def create_task(client, headers, section_id: str) -> dict:
    response = await client.post(
        f"/api/admin/sections/{section_id}/tasks",
        headers=headers,
        json={
            "title": "HTTP method",
            "statement": "Enter the method used for reading a resource.",
            "position": 1,
            "check_type": "exact_match",
            "expected_answer": "GET",
            "max_attempts": 2,
            "reward_points": 5,
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_code_task(client, headers, section_id: str) -> dict:
    response = await client.post(
        f"/api/admin/sections/{section_id}/code-tasks",
        headers=headers,
        json={
            "title": "Sum numbers",
            "statement": "Read two integers and print their sum.",
            "position": 2,
            "language": "python",
            "starter_code": "print(1)",
            "max_attempts": 2,
            "reward_points": 5,
            "time_limit_seconds": 2,
            "memory_limit_mb": 128,
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_test_case(client, headers, code_task_id: str, position: int) -> dict:
    response = await client.post(
        f"/api/admin/code-tasks/{code_task_id}/test-cases",
        headers=headers,
        json={
            "position": position,
            "input_data": f"{position} {position}",
            "expected_output": str(position + position),
            "is_hidden": False,
            "explanation": "",
        },
    )
    assert response.status_code == 201
    return response.json()


async def get_section_structure(client, course_id: str) -> dict:
    response = await client.get(f"/api/courses/{course_id}/structure")
    assert response.status_code == 200
    return response.json()["modules"][0]["sections"][0]


@pytest.mark.asyncio
async def test_author_removes_content_before_any_learning_history(
    client,
    author_auth_headers,
) -> None:
    tree = await create_authoring_tree(client, author_auth_headers)
    task = await create_task(client, author_auth_headers, tree["section_id"])
    code_task = await create_code_task(client, author_auth_headers, tree["section_id"])
    first_case = await create_test_case(
        client, author_auth_headers, code_task["id"], position=1
    )
    await create_test_case(client, author_auth_headers, code_task["id"], position=2)

    section = await get_section_structure(client, tree["course_id"])
    assert section["task_ids"] == [task["id"]]
    assert section["code_task_ids"] == [code_task["id"]]

    remove_task_response = await client.delete(
        f"/api/admin/tasks/{task['id']}",
        headers=author_auth_headers,
    )
    assert remove_task_response.status_code == 204

    remove_case_response = await client.delete(
        f"/api/admin/test-cases/{first_case['id']}",
        headers=author_auth_headers,
    )
    assert remove_case_response.status_code == 204

    code_task_read = await client.get(f"/api/code-tasks/{code_task['id']}")
    assert code_task_read.status_code == 200

    remove_code_task_response = await client.delete(
        f"/api/admin/code-tasks/{code_task['id']}",
        headers=author_auth_headers,
    )
    assert remove_code_task_response.status_code == 204

    section = await get_section_structure(client, tree["course_id"])
    assert section["task_ids"] == []
    assert section["tasks"] == []
    assert section["code_task_ids"] == []
    assert section["code_tasks"] == []

    assert (await client.get(f"/api/tasks/{task['id']}")).status_code == 404
    assert (await client.get(f"/api/code-tasks/{code_task['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_author_cannot_remove_content_after_student_activity(
    client,
    author_auth_headers,
    student_auth_headers,
    fake_submission_queue,
) -> None:
    tree = await create_authoring_tree(client, author_auth_headers)
    task = await create_task(client, author_auth_headers, tree["section_id"])
    code_task = await create_code_task(client, author_auth_headers, tree["section_id"])
    await create_test_case(client, author_auth_headers, code_task["id"], position=1)

    attempt_response = await client.post(
        f"/api/learning/tasks/{task['id']}/attempts",
        headers=student_auth_headers,
        json={"submitted_answer": "GET"},
    )
    assert attempt_response.status_code == 201

    submission_response = await client.post(
        f"/api/learning/code-tasks/{code_task['id']}/submissions",
        headers=student_auth_headers,
        json={"source_code": "print(1)"},
    )
    assert submission_response.status_code == 202
    assert fake_submission_queue.items

    remove_task_response = await client.delete(
        f"/api/admin/tasks/{task['id']}",
        headers=author_auth_headers,
    )
    assert remove_task_response.status_code == 400
    assert remove_task_response.json()["error"] == "application_error"

    remove_code_task_response = await client.delete(
        f"/api/admin/code-tasks/{code_task['id']}",
        headers=author_auth_headers,
    )
    assert remove_code_task_response.status_code == 400
    assert remove_code_task_response.json()["error"] == "application_error"

    section = await get_section_structure(client, tree["course_id"])
    assert section["task_ids"] == [task["id"]]
    assert section["code_task_ids"] == [code_task["id"]]

    assert (await client.get(f"/api/tasks/{task['id']}")).status_code == 200
    assert (await client.get(f"/api/code-tasks/{code_task['id']}")).status_code == 200


@pytest.mark.asyncio
async def test_author_cannot_remove_test_case_after_first_submission(
    client,
    author_auth_headers,
    student_auth_headers,
    fake_submission_queue,
) -> None:
    tree = await create_authoring_tree(client, author_auth_headers)
    code_task = await create_code_task(client, author_auth_headers, tree["section_id"])
    first_case = await create_test_case(
        client, author_auth_headers, code_task["id"], position=1
    )
    second_case = await create_test_case(
        client, author_auth_headers, code_task["id"], position=2
    )

    first_removal = await client.delete(
        f"/api/admin/test-cases/{first_case['id']}",
        headers=author_auth_headers,
    )
    assert first_removal.status_code == 204

    submission_response = await client.post(
        f"/api/learning/code-tasks/{code_task['id']}/submissions",
        headers=student_auth_headers,
        json={"source_code": "print(2)"},
    )
    assert submission_response.status_code == 202

    second_removal = await client.delete(
        f"/api/admin/test-cases/{second_case['id']}",
        headers=author_auth_headers,
    )
    assert second_removal.status_code == 400
    assert second_removal.json()["error"] == "application_error"

    code_task_read = await client.get(f"/api/code-tasks/{code_task['id']}")
    assert code_task_read.status_code == 200
