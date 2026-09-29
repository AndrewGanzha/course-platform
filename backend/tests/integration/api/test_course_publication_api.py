import pytest


@pytest.mark.asyncio
async def test_publication_readiness_endpoint_reports_missing_modules(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Draft course",
            "description": "Publication diagnostics.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.get(
        f"/api/admin/courses/{course_id}/publication-readiness",
        headers=author_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_ready"] is False
    assert payload["issues"][0]["code"] == "course_without_modules"


@pytest.mark.asyncio
async def test_publish_returns_diagnostics_when_course_is_not_ready(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Draft course",
            "description": "Publication diagnostics.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] == "course_publication_not_ready"
    assert payload["issues"][0]["code"] == "course_without_modules"


@pytest.mark.asyncio
async def test_publish_succeeds_for_minimally_complete_course(
    client,
    author_auth_headers,
):
    course_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Ready course",
            "description": "Ready for publication.",
        },
    )
    course_id = course_response.json()["id"]

    module_response = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=author_auth_headers,
        json={
            "title": "Module 1",
            "description": "Description",
            "position": 1,
        },
    )
    module_id = module_response.json()["id"]

    section_response = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=author_auth_headers,
        json={
            "title": "Section 1",
            "description": "Description",
            "position": 1,
        },
    )
    section_id = section_response.json()["id"]

    await client.post(
        f"/api/admin/sections/{section_id}/lectures",
        headers=author_auth_headers,
        json={
            "title": "Lecture 1",
            "content": "Lecture content",
            "position": 1,
        },
    )

    publish_response = await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )

    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"
