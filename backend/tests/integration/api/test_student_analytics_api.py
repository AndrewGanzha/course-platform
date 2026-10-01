import pytest


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
