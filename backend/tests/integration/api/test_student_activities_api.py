import pytest
from sqlalchemy import select

import app.presentation.api.dependencies as api_dependencies
from app.application.use_cases.code_submissions.complete_code_submission import (
    CompleteCodeSubmissionCommand,
    CompleteCodeSubmissionUseCase,
)
from app.domain.entities.execution_result import ExecutionStatus
from app.infrastructure.database.models import StudentActivityModel
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


async def _activities(session_factory) -> list[StudentActivityModel]:
    async with session_factory() as session:
        result = await session.execute(select(StudentActivityModel))
        return list(result.scalars().all())


@pytest.mark.asyncio
async def test_question_completion_records_activities(
    client,
    student_auth_headers,
    session_factory,
    seeded_interactive_tree,
):
    response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.correct_option_id]},
    )
    assert response.status_code == 201

    activities = await _activities(session_factory)
    types = [activity.activity_type for activity in activities]
    assert types.count("question_completed") == 1
    assert types.count("section_completed") == 1
    assert types.count("module_completed") == 1

    question_activity = next(
        activity
        for activity in activities
        if activity.activity_type == "question_completed"
    )
    assert question_activity.entity_id == seeded_interactive_tree.question_id
    assert question_activity.course_id == seeded_interactive_tree.course_id
    assert question_activity.details["awarded_points"] == 5


@pytest.mark.asyncio
async def test_repeat_completion_does_not_duplicate_activity(
    client,
    student_auth_headers,
    session_factory,
    seeded_interactive_tree,
):
    # A wrong attempt must not create a completion activity.
    wrong_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.wrong_option_id]},
    )
    assert wrong_response.status_code == 201

    correct_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.correct_option_id]},
    )
    assert correct_response.status_code == 201

    activities = await _activities(session_factory)
    types = [activity.activity_type for activity in activities]
    assert types.count("question_completed") == 1
    assert types.count("section_completed") == 1
    assert types.count("module_completed") == 1


@pytest.mark.asyncio
async def test_code_task_completion_records_activity(
    client,
    student_auth_headers,
    session_factory,
    fake_submission_queue,
    seeded_code_task_tree,
):
    submission_response = await client.post(
        f"/api/learning/code-tasks/{seeded_code_task_tree.code_task_id}/submissions",
        headers=student_auth_headers,
        json={"source_code": "print(5)"},
    )
    assert submission_response.status_code == 202
    submission_id = submission_response.json()["id"]

    uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
    await CompleteCodeSubmissionUseCase(uow=uow).execute(
        CompleteCodeSubmissionCommand(
            submission_id=submission_id,
            status=ExecutionStatus.PASSED,
            passed_test_cases=1,
            total_test_cases=1,
        )
    )

    activities = await _activities(session_factory)
    types = [activity.activity_type for activity in activities]
    assert types.count("code_task_completed") == 1
    assert types.count("section_completed") == 1
    assert types.count("module_completed") == 1

    code_task_activity = next(
        activity
        for activity in activities
        if activity.activity_type == "code_task_completed"
    )
    assert code_task_activity.entity_id == seeded_code_task_tree.code_task_id


@pytest.mark.asyncio
async def test_course_review_records_create_and_update_activities(
    client,
    student_auth_headers,
    session_factory,
    seeded_review_eligibility,
):
    course_id = seeded_review_eligibility.eligible_course_id

    await client.put(
        f"/api/courses/{course_id}/reviews/me",
        headers=student_auth_headers,
        json={"rating": 4, "text": "Good."},
    )
    await client.put(
        f"/api/courses/{course_id}/reviews/me",
        headers=student_auth_headers,
        json={"rating": 5, "text": "Better now."},
    )

    activities = await _activities(session_factory)
    types = [activity.activity_type for activity in activities]
    assert types.count("course_review_created") == 1
    assert types.count("course_review_updated") == 1


@pytest.mark.asyncio
async def test_my_activities_returns_own_history_paginated(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.correct_option_id]},
    )

    response = await client.get(
        "/api/profile/me/activities",
        headers=student_auth_headers,
        params={"limit": 2, "offset": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert payload["limit"] == 2
    assert payload["offset"] == 0
    assert len(payload["items"]) == 2


@pytest.mark.asyncio
async def test_my_activities_requires_student_role(
    client,
    author_auth_headers,
):
    response = await client.get(
        "/api/profile/me/activities",
        headers=author_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_can_read_platform_activities(
    client,
    student_auth_headers,
    admin_auth_headers,
    seeded_interactive_tree,
):
    await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.correct_option_id]},
    )

    response = await client.get(
        "/api/admin/activities",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 3


@pytest.mark.asyncio
async def test_platform_activities_require_admin(
    client,
    student_auth_headers,
):
    response = await client.get(
        "/api/admin/activities",
        headers=student_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_author_reads_activities_of_own_courses_only(
    client,
    student_auth_headers,
    author_auth_headers,
    seeded_interactive_tree,
):
    await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.correct_option_id]},
    )

    response = await client.get(
        "/api/profile/me/teaching/activities",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 3


@pytest.mark.asyncio
async def test_foreign_author_cannot_read_course_activities(
    client,
    student_auth_headers,
    other_author_auth_headers,
    seeded_interactive_tree,
):
    await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={"selected_option_ids": [seeded_interactive_tree.correct_option_id]},
    )

    response = await client.get(
        "/api/profile/me/teaching/activities",
        headers=other_author_auth_headers,
        params={"course_id": seeded_interactive_tree.course_id},
    )

    assert response.status_code == 403
