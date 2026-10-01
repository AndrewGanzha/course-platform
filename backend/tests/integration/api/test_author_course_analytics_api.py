import pytest


@pytest.mark.asyncio
async def test_author_can_get_own_course_analytics(
    client,
    author_auth_headers,
    seeded_author_analytics_tree,
):
    response = await client.get(
        f"/api/profile/me/teaching/courses/"
        f"{seeded_author_analytics_tree.course_id}/analytics",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["course_id"] == seeded_author_analytics_tree.course_id
    assert payload["course_title"] == seeded_author_analytics_tree.course_title


@pytest.mark.asyncio
async def test_foreign_author_cannot_get_course_analytics(
    client,
    other_author_auth_headers,
    seeded_author_analytics_tree,
):
    response = await client.get(
        f"/api/profile/me/teaching/courses/"
        f"{seeded_author_analytics_tree.course_id}/analytics",
        headers=other_author_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_can_get_foreign_course_analytics(
    client,
    admin_auth_headers,
    seeded_author_analytics_tree,
):
    response = await client.get(
        f"/api/profile/me/teaching/courses/"
        f"{seeded_author_analytics_tree.course_id}/analytics",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["course_id"] == seeded_author_analytics_tree.course_id


@pytest.mark.asyncio
async def test_author_course_analytics_returns_progress_and_difficult_items(
    client,
    author_auth_headers,
    seeded_author_analytics_tree,
):
    response = await client.get(
        f"/api/profile/me/teaching/courses/"
        f"{seeded_author_analytics_tree.course_id}/analytics",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["students_started_count"] == 2
    assert payload["students_completed_count"] == 1
    assert payload["completion_rate"] == 0.5
    assert payload["average_completion_ratio"] == 0.5
    assert payload["average_points"] == 10.5

    assert len(payload["modules"]) == 1
    assert payload["modules"][0]["students_completed_count"] == 1

    assert len(payload["difficult_questions"]) == 1
    question = payload["difficult_questions"][0]
    assert question["question_id"] == seeded_author_analytics_tree.question_id
    assert question["students_count"] == 2
    assert question["attempts_count"] == 3
    assert question["first_try_success_rate"] == 0.5
    assert question["average_attempts_per_student"] == 1.5

    assert len(payload["difficult_tasks"]) == 1
    task = payload["difficult_tasks"][0]
    assert task["task_id"] == seeded_author_analytics_tree.task_id
    assert task["first_try_success_rate"] == 0.5

    assert len(payload["problematic_code_tasks"]) == 1
    code_task = payload["problematic_code_tasks"][0]
    assert code_task["code_task_id"] == seeded_author_analytics_tree.code_task_id
    assert code_task["submissions_count"] == 3
    assert code_task["passed_students_count"] == 1
    assert code_task["pass_rate"] == 0.5
    assert code_task["repeat_students_count"] == 1
