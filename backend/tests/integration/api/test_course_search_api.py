import pytest


async def create_minimally_ready_course(
    client,
    author_auth_headers,
    *,
    title: str,
    description: str,
    short_description: str,
) -> str:
    course_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": title,
            "description": description,
            "short_description": short_description,
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

    await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )
    return course_id


@pytest.mark.asyncio
async def test_search_returns_matching_published_course(
    client,
    author_auth_headers,
):
    await create_minimally_ready_course(
        client,
        author_auth_headers,
        title="FastAPI Advanced",
        description="Deep dive into async backend architecture.",
        short_description="Build production APIs.",
    )
    await create_minimally_ready_course(
        client,
        author_auth_headers,
        title="Docker Basics",
        description="Containers for backend developers.",
        short_description="Learn container fundamentals.",
    )

    response = await client.get("/api/courses?search=fastapi")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "FastAPI Advanced"


@pytest.mark.asyncio
async def test_search_is_case_insensitive_and_trims_spaces(
    client,
    author_auth_headers,
):
    await create_minimally_ready_course(
        client,
        author_auth_headers,
        title="FastAPI Advanced",
        description="Deep dive into async backend architecture.",
        short_description="Build production APIs.",
    )

    response = await client.get("/api/courses?search=  FASTAPI  ")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "FastAPI Advanced"


@pytest.mark.asyncio
async def test_search_does_not_return_draft_courses(
    client,
    author_auth_headers,
):
    await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Hidden FastAPI Draft",
            "description": "Should not appear in public search.",
            "short_description": "Still private.",
        },
    )

    response = await client.get("/api/courses?search=fastapi")

    assert response.status_code == 200
    assert response.json() == []
