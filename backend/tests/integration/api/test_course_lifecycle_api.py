import pytest


async def create_publishable_course(
    client,
    headers,
    title: str,
    description: str,
) -> str:
    create_response = await client.post(
        "/api/admin/courses",
        headers=headers,
        json={
            "title": title,
            "description": description,
        },
    )
    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    module_response = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=headers,
        json={
            "title": "Module",
            "description": "Module with content.",
            "position": 1,
        },
    )
    module_id = module_response.json()["id"]

    section_response = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=headers,
        json={
            "title": "Section",
            "description": "Section with a lecture.",
            "position": 1,
        },
    )
    section_id = section_response.json()["id"]

    lecture_response = await client.post(
        f"/api/admin/sections/{section_id}/lectures",
        headers=headers,
        json={
            "title": "Lecture",
            "content": "Lecture content.",
            "position": 1,
        },
    )
    assert lecture_response.status_code == 201

    return course_id


@pytest.mark.asyncio
async def test_publish_course_endpoint_changes_status(
    client,
    author_auth_headers,
):
    course_id = await create_publishable_course(
        client,
        author_auth_headers,
        title="Lifecycle course",
        description="Course for lifecycle checks.",
    )

    publish_response = await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"


@pytest.mark.asyncio
async def test_publish_course_endpoint_rejects_incomplete_course(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Incomplete course",
            "description": "Course without any modules.",
        },
    )
    course_id = create_response.json()["id"]

    publish_response = await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    assert publish_response.status_code == 400
    payload = publish_response.json()
    assert payload["error"] == "course_not_ready"
    assert payload["readiness"]["course_id"] == course_id
    assert payload["readiness"]["is_ready"] is False
    assert payload["readiness"]["issues"][0]["code"] == "course_without_modules"


@pytest.mark.asyncio
async def test_get_course_publication_readiness_reports_issues(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Incomplete course",
            "description": "Course without any modules.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.get(
        f"/api/admin/courses/{course_id}/publication-readiness",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["course_id"] == course_id
    assert payload["is_ready"] is False
    assert len(payload["issues"]) == 1
    assert payload["issues"][0]["code"] == "course_without_modules"


@pytest.mark.asyncio
async def test_get_course_publication_readiness_confirms_ready_course(
    client,
    author_auth_headers,
):
    course_id = await create_publishable_course(
        client,
        author_auth_headers,
        title="Ready course",
        description="Course with a complete tree.",
    )

    response = await client.get(
        f"/api/admin/courses/{course_id}/publication-readiness",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["course_id"] == course_id
    assert payload["is_ready"] is True
    assert payload["issues"] == []


@pytest.mark.asyncio
async def test_archive_course_endpoint_changes_status(
    client,
    author_auth_headers,
):
    course_id = await create_publishable_course(
        client,
        author_auth_headers,
        title="Course to archive",
        description="Initially published course.",
    )

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

    published_course_id = await create_publishable_course(
        client,
        author_auth_headers,
        title="Published course",
        description="Visible for students.",
    )

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
    course_id = await create_publishable_course(
        client,
        author_auth_headers,
        title="Archived course",
        description="Was published earlier.",
    )

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
    course_id = await create_publishable_course(
        client,
        author_auth_headers,
        title="Published course",
        description="Visible for students.",
    )

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
