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
            "difficulty": "advanced",
            "tag_names": ["FastAPI", "python", "backend"],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["short_description"] == "Build production-grade APIs."
    assert payload["cover_image_url"] is None
    assert payload["difficulty"] == "advanced"
    assert payload["tag_names"] == ["fastapi", "python", "backend"]


@pytest.mark.asyncio
async def test_update_course_changes_metadata_and_keeps_cover(
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

    cover_response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\npayload", "image/png")},
    )
    assert cover_response.status_code == 200
    cover_url = cover_response.json()["cover_image_url"]

    update_response = await client.put(
        f"/api/admin/courses/{course_id}",
        headers=author_auth_headers,
        json={
            "title": "Metadata course",
            "description": "Updated description.",
            "short_description": "Short preview.",
            "difficulty": "intermediate",
            "tag_names": ["Backend", "FastAPI", "backend"],
        },
    )

    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["short_description"] == "Short preview."
    assert payload["difficulty"] == "intermediate"
    assert payload["tag_names"] == ["backend", "fastapi"]
    assert payload["cover_image_url"] == cover_url
