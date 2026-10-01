from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_get_my_course_analytics_requires_authentication(
    client,
    seeded_course_tree,
):
    response = await client.get(
        f"/api/profile/me/courses/{seeded_course_tree.course_id}/analytics"
    )

    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"


@pytest.mark.asyncio
async def test_get_my_course_analytics_returns_empty_progress(
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
    assert payload["course_title"] == seeded_course_tree.course_title
    assert payload["completion_ratio"] == 0.0
    assert payload["is_completed"] is False
    assert payload["total_points"] == 0
    assert payload["completed_modules_count"] == 0
    assert payload["total_modules_count"] == 1
    assert payload["completed_sections_count"] == 0
    assert payload["total_sections_count"] == 1
    assert [module["module_id"] for module in payload["modules"]] == [
        seeded_course_tree.module_id
    ]
    assert payload["modules"][0]["is_completed"] is False
    assert payload["weak_questions"] == []
    assert payload["weak_tasks"] == []


@pytest.mark.asyncio
async def test_get_my_course_analytics_rejects_non_student(
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
async def test_get_my_course_analytics_returns_404_for_unknown_course(
    client,
    student_auth_headers,
):
    response = await client.get(
        f"/api/profile/me/courses/{uuid4()}/analytics",
        headers=student_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "course_not_found"
