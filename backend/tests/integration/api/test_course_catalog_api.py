import pytest


@pytest.mark.asyncio
async def test_draft_course_is_hidden_from_public_course_card(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Draft catalog course",
            "description": "Still private.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.get(f"/api/courses/{course_id}")

    assert response.status_code == 404
    assert response.json()["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_author_can_read_own_draft_course_card(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Draft catalog course",
            "description": "Visible for owner.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.get(
        f"/api/courses/{course_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == course_id
    assert payload["status"] == "draft"
    assert payload["counters"]["module_count"] == 0
    assert payload["modules"] == []
