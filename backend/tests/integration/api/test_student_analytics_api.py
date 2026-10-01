import pytest

import app.presentation.api.dependencies as api_dependencies
from app.application.use_cases.code_submissions.complete_code_submission import (
    CompleteCodeSubmissionCommand,
    CompleteCodeSubmissionUseCase,
)
from app.domain.entities.execution_result import ExecutionStatus
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


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


@pytest.mark.asyncio
async def test_student_analytics_returns_empty_progress_for_not_started_course(
    client,
    student_auth_headers,
    seeded_course_tree,
):
    response = await client.get(
        f"/api/profile/me/courses/{seeded_course_tree.course_id}/analytics",
        headers=student_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["course_id"] == seeded_course_tree.course_id
    assert payload["completion_ratio"] == 0.0
    assert payload["is_completed"] is False
    assert payload["total_points"] == 0
    assert payload["completed_modules_count"] == 0
    assert payload["completed_sections_count"] == 0
    assert payload["weak_questions"] == []
    assert payload["weak_tasks"] == []


@pytest.mark.asyncio
async def test_student_analytics_returns_points_and_completion_after_successful_learning(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    attempt_context = await client.get(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempt",
        headers=student_auth_headers,
    )
    assert attempt_context.status_code == 200

    submit_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={
            "selected_option_ids": [seeded_interactive_tree.correct_option_id],
        },
    )
    assert submit_response.status_code == 201

    analytics_response = await client.get(
        f"/api/profile/me/courses/{seeded_interactive_tree.course_id}/analytics",
        headers=student_auth_headers,
    )
    assert analytics_response.status_code == 200
    payload = analytics_response.json()
    assert payload["total_points"] == 5
    assert payload["completed_sections_count"] >= 1
    assert payload["completion_ratio"] > 0.0


@pytest.mark.asyncio
async def test_student_analytics_includes_weak_questions_after_multiple_attempts(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    wrong_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={
            "selected_option_ids": [seeded_interactive_tree.wrong_option_id],
        },
    )
    assert wrong_response.status_code == 201

    correct_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={
            "selected_option_ids": [seeded_interactive_tree.correct_option_id],
        },
    )
    assert correct_response.status_code == 201

    analytics_response = await client.get(
        f"/api/profile/me/courses/{seeded_interactive_tree.course_id}/analytics",
        headers=student_auth_headers,
    )
    assert analytics_response.status_code == 200
    payload = analytics_response.json()
    assert len(payload["weak_questions"]) == 1
    assert (
        payload["weak_questions"][0]["question_id"]
        == seeded_interactive_tree.question_id
    )
    assert payload["weak_questions"][0]["attempts_count"] == 2


@pytest.mark.asyncio
async def test_student_analytics_forbidden_for_non_student_user(
    client,
    author_auth_headers,
    seeded_course_tree,
):
    response = await client.get(
        f"/api/profile/me/courses/{seeded_course_tree.course_id}/analytics",
        headers=author_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_student_analytics_returns_empty_weak_code_tasks_without_submissions(
    client,
    student_auth_headers,
    seeded_code_task_tree,
):
    response = await client.get(
        f"/api/profile/me/courses/{seeded_code_task_tree.course_id}/analytics",
        headers=student_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["weak_code_tasks"] == []


@pytest.mark.asyncio
async def test_student_analytics_includes_weak_code_task_after_multiple_attempts(
    client,
    student_auth_headers,
    seeded_code_task_tree,
    fake_submission_queue,
):
    first_submission = await client.post(
        f"/api/learning/code-tasks/{seeded_code_task_tree.code_task_id}/submissions",
        headers=student_auth_headers,
        json={"source_code": "print(1)"},
    )
    assert first_submission.status_code == 202

    second_submission = await client.post(
        f"/api/learning/code-tasks/{seeded_code_task_tree.code_task_id}/submissions",
        headers=student_auth_headers,
        json={"source_code": "a, b = map(int, input().split())\nprint(a + b)"},
    )
    assert second_submission.status_code == 202

    analytics_response = await client.get(
        f"/api/profile/me/courses/{seeded_code_task_tree.course_id}/analytics",
        headers=student_auth_headers,
    )
    assert analytics_response.status_code == 200
    payload = analytics_response.json()
    assert len(payload["weak_code_tasks"]) == 1
    assert (
        payload["weak_code_tasks"][0]["code_task_id"]
        == seeded_code_task_tree.code_task_id
    )
    assert (
        payload["weak_code_tasks"][0]["section_id"] == seeded_code_task_tree.section_id
    )
    assert payload["weak_code_tasks"][0]["attempts_count"] == 2


@pytest.mark.asyncio
async def test_student_analytics_includes_weak_code_task_after_failed_run(
    client,
    student_auth_headers,
    session_factory,
    fake_submission_queue,
    seeded_code_task_tree,
):
    submission_response = await client.post(
        f"/api/learning/code-tasks/{seeded_code_task_tree.code_task_id}/submissions",
        headers=student_auth_headers,
        json={"source_code": "print(1)"},
    )
    assert submission_response.status_code == 202
    submission_id = submission_response.json()["id"]

    uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
    complete_use_case = CompleteCodeSubmissionUseCase(uow=uow)
    await complete_use_case.execute(
        CompleteCodeSubmissionCommand(
            submission_id=submission_id,
            status=ExecutionStatus.FAILED,
        )
    )

    analytics_response = await client.get(
        f"/api/profile/me/courses/{seeded_code_task_tree.course_id}/analytics",
        headers=student_auth_headers,
    )
    assert analytics_response.status_code == 200
    payload = analytics_response.json()
    assert len(payload["weak_code_tasks"]) == 1
    assert (
        payload["weak_code_tasks"][0]["code_task_id"]
        == seeded_code_task_tree.code_task_id
    )
    assert payload["weak_code_tasks"][0]["attempts_count"] == 1
