import pytest


async def create_published_course(
    client,
    author_auth_headers,
    *,
    title: str,
    description: str,
    short_description: str,
    difficulty: str,
    tag_names: list[str],
) -> str:
    course_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": title,
            "description": description,
            "short_description": short_description,
            "difficulty": difficulty,
            "tag_names": tag_names,
        },
    )
    assert course_response.status_code == 201
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
    return course_id


@pytest.mark.asyncio
async def test_catalog_filters_courses_by_difficulty(
    client,
    author_auth_headers,
):
    await create_published_course(
        client,
        author_auth_headers,
        title="FastAPI for beginners",
        description="First backend course.",
        short_description="Start backend development.",
        difficulty="beginner",
        tag_names=["python", "backend"],
    )
    await create_published_course(
        client,
        author_auth_headers,
        title="Advanced architecture",
        description="Deep dive into scaling.",
        short_description="System design and scaling.",
        difficulty="advanced",
        tag_names=["architecture", "backend"],
    )

    response = await client.get("/api/courses?difficulty=beginner")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "FastAPI for beginners"
    assert payload[0]["difficulty"] == "beginner"


@pytest.mark.asyncio
async def test_catalog_filters_courses_by_single_tag(
    client,
    author_auth_headers,
):
    await create_published_course(
        client,
        author_auth_headers,
        title="FastAPI backend",
        description="API course.",
        short_description="Backend APIs.",
        difficulty="intermediate",
        tag_names=["fastapi", "backend"],
    )
    await create_published_course(
        client,
        author_auth_headers,
        title="Docker basics",
        description="Containers course.",
        short_description="Learn Docker.",
        difficulty="beginner",
        tag_names=["docker", "devops"],
    )

    response = await client.get("/api/courses?tag=backend")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "FastAPI backend"
    assert payload[0]["tag_names"] == ["fastapi", "backend"]


@pytest.mark.asyncio
async def test_catalog_filters_courses_by_all_requested_tags(
    client,
    author_auth_headers,
):
    await create_published_course(
        client,
        author_auth_headers,
        title="FastAPI backend",
        description="API course.",
        short_description="Backend APIs.",
        difficulty="intermediate",
        tag_names=["fastapi", "backend", "python"],
    )
    await create_published_course(
        client,
        author_auth_headers,
        title="Python basics",
        description="Intro course.",
        short_description="Learn Python.",
        difficulty="beginner",
        tag_names=["python"],
    )

    response = await client.get("/api/courses?tag=python&tag=backend")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "FastAPI backend"


@pytest.mark.asyncio
async def test_catalog_combines_search_and_filters(
    client,
    author_auth_headers,
):
    await create_published_course(
        client,
        author_auth_headers,
        title="FastAPI backend",
        description="Intermediate API architecture.",
        short_description="Build backend services.",
        difficulty="intermediate",
        tag_names=["fastapi", "backend"],
    )
    await create_published_course(
        client,
        author_auth_headers,
        title="FastAPI advanced",
        description="Advanced scaling and internals.",
        short_description="Deep framework internals.",
        difficulty="advanced",
        tag_names=["fastapi", "backend"],
    )

    response = await client.get(
        "/api/courses?search=fastapi&difficulty=intermediate&tag=backend"
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "FastAPI backend"
    assert payload[0]["difficulty"] == "intermediate"


@pytest.mark.asyncio
async def test_catalog_filters_do_not_expose_draft_courses(
    client,
    author_auth_headers,
):
    await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Hidden FastAPI draft",
            "description": "Should stay private.",
            "short_description": "Still private.",
            "difficulty": "intermediate",
            "tag_names": ["fastapi", "backend"],
        },
    )

    response = await client.get(
        "/api/courses?search=fastapi&difficulty=intermediate&tag=backend"
    )

    assert response.status_code == 200
    assert response.json() == []
