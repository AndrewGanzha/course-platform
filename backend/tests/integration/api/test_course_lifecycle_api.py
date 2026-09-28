import pytest


@pytest.mark.asyncio
async def test_publish_course_endpoint_changes_status(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Lifecycle course",
            "description": "Course for lifecycle checks.",
        },
    )
    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    publish_response = await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"


@pytest.mark.asyncio
async def test_archive_course_endpoint_changes_status(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Course to archive",
            "description": "Initially published course.",
        },
    )
    course_id = create_response.json()["id"]

    await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    archive_response = await client.post(
        f"/api/admin/courses/{course_id}/archive",
        headers=author_auth_headers,
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"


@pytest.mark.asyncio
async def test_public_courses_list_returns_only_published_courses(
    client,
    author_auth_headers,
):
    await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Draft course",
            "description": "Hidden from students.",
        },
    )

    published_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Published course",
            "description": "Visible for students.",
        },
    )
    published_course_id = published_response.json()["id"]

    await client.post(
        f"/api/admin/courses/{published_course_id}/publish",
        headers=author_auth_headers,
    )

    response = await client.get("/api/courses")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Published course"
    assert payload[0]["status"] == "published"


@pytest.mark.asyncio
async def test_draft_course_is_hidden_from_public_get(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Draft course",
            "description": "Still in progress.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.get(f"/api/courses/{course_id}")

    assert response.status_code == 404
    assert response.json()["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_archived_course_is_hidden_from_public_get(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Archived course",
            "description": "Was published earlier.",
        },
    )
    course_id = create_response.json()["id"]

    await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )
    await client.post(
        f"/api/admin/courses/{course_id}/archive",
        headers=author_auth_headers,
    )

    response = await client.get(f"/api/courses/{course_id}")

    assert response.status_code == 404
    assert response.json()["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_published_course_can_still_be_updated(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Published course",
            "description": "Visible for students.",
        },
    )
    course_id = create_response.json()["id"]

    await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    update_response = await client.put(
        f"/api/admin/courses/{course_id}",
        headers=author_auth_headers,
        json={
            "title": "Updated published course",
            "description": "Still visible and still editable.",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated published course"
    assert update_response.json()["status"] == "published"
