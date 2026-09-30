import pytest


@pytest.mark.asyncio
async def test_create_course_accepts_metadata(
    client,
    author_auth_headers,
):
    response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "FastAPI Advanced",
            "description": "Detailed course description.",
            "short_description": "Build production-grade APIs.",
            "cover_image_url": "https://example.com/course-cover.png",
            "difficulty": "advanced",
            "tag_names": ["FastAPI", "python", "backend"],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["short_description"] == "Build production-grade APIs."
    assert payload["cover_image_url"] == "https://example.com/course-cover.png"
    assert payload["difficulty"] == "advanced"
    assert payload["tag_names"] == ["fastapi", "python", "backend"]


@pytest.mark.asyncio
async def test_update_course_changes_metadata(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Metadata course",
            "description": "Initial description.",
        },
    )
    course_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/admin/courses/{course_id}",
        headers=author_auth_headers,
        json={
            "title": "Metadata course",
            "description": "Updated description.",
            "short_description": "Short preview.",
            "cover_image_url": "https://example.com/new-cover.png",
            "difficulty": "intermediate",
            "tag_names": ["Backend", "FastAPI", "backend"],
        },
    )

    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["short_description"] == "Short preview."
    assert payload["cover_image_url"] == "https://example.com/new-cover.png"
    assert payload["difficulty"] == "intermediate"
    assert payload["tag_names"] == ["backend", "fastapi"]
