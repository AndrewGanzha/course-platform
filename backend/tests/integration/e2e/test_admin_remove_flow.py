import pytest


@pytest.mark.asyncio
async def test_admin_can_remove_an_entire_course_tree_incrementally(
    client,
    seeded_admin_user,
) -> None:
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "admin@example.com",
            "password": "strongpassword123",
        },
    )
    assert login_response.status_code == 200
    headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    course_response = await client.post(
        "/api/admin/courses",
        headers=headers,
        json={
            "title": "Course removal lifecycle",
            "description": "Content created and removed through the API.",
        },
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    control_course_response = await client.post(
        "/api/admin/courses",
        headers=headers,
        json={
            "title": "Control course",
            "description": "Must survive removal of another course.",
        },
    )
    assert control_course_response.status_code == 201
    control_course_id = control_course_response.json()["id"]

    module_response = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=headers,
        json={
            "title": "Disposable module",
            "description": "A module used by the removal flow.",
            "position": 1,
        },
    )
    assert module_response.status_code == 201
    module_id = module_response.json()["id"]

    section_response = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=headers,
        json={
            "title": "Disposable section",
            "description": "A section used by the removal flow.",
            "position": 1,
        },
    )
    assert section_response.status_code == 201
    section_id = section_response.json()["id"]

    lecture_response = await client.post(
        f"/api/admin/sections/{section_id}/lectures",
        headers=headers,
        json={
            "title": "Disposable lecture",
            "content": "This lecture will be removed through the admin API.",
            "position": 1,
        },
    )
    assert lecture_response.status_code == 201
    lecture_id = lecture_response.json()["id"]

    courses_response = await client.get("/api/courses")
    assert courses_response.status_code == 200
    assert {course["id"] for course in courses_response.json()} == {
        course_id,
        control_course_id,
    }

    course_read_response = await client.get(f"/api/courses/{course_id}")
    assert course_read_response.status_code == 200
    assert course_read_response.json()["title"] == "Course removal lifecycle"

    structure_response = await client.get(f"/api/courses/{course_id}/structure")
    assert structure_response.status_code == 200
    structure = structure_response.json()
    assert [module["id"] for module in structure["modules"]] == [module_id]
    assert [
        section["id"] for section in structure["modules"][0]["sections"]
    ] == [section_id]
    assert [
        lecture["id"]
        for lecture in structure["modules"][0]["sections"][0]["lectures"]
    ] == [lecture_id]

    lecture_read_response = await client.get(f"/api/lectures/{lecture_id}")
    assert lecture_read_response.status_code == 200
    assert (
        lecture_read_response.json()["content"]
        == "This lecture will be removed through the admin API."
    )

    remove_lecture_response = await client.delete(
        f"/api/admin/lectures/{lecture_id}",
        headers=headers,
    )
    assert remove_lecture_response.status_code == 204
    assert remove_lecture_response.content == b""

    removed_lecture_response = await client.get(f"/api/lectures/{lecture_id}")
    assert removed_lecture_response.status_code == 404
    assert removed_lecture_response.json()["error"] == "lecture_not_found"

    structure_response = await client.get(f"/api/courses/{course_id}/structure")
    assert structure_response.status_code == 200
    assert structure_response.json()["modules"][0]["sections"][0]["lectures"] == []

    remove_section_response = await client.delete(
        f"/api/admin/sections/{section_id}",
        headers=headers,
    )
    assert remove_section_response.status_code == 204
    assert remove_section_response.content == b""

    structure_response = await client.get(f"/api/courses/{course_id}/structure")
    assert structure_response.status_code == 200
    assert structure_response.json()["modules"][0]["sections"] == []

    remove_module_response = await client.delete(
        f"/api/admin/modules/{module_id}",
        headers=headers,
    )
    assert remove_module_response.status_code == 204
    assert remove_module_response.content == b""

    structure_response = await client.get(f"/api/courses/{course_id}/structure")
    assert structure_response.status_code == 200
    assert structure_response.json()["modules"] == []

    course_read_response = await client.get(f"/api/courses/{course_id}")
    assert course_read_response.status_code == 200

    remove_course_response = await client.delete(
        f"/api/admin/courses/{course_id}",
        headers=headers,
    )
    assert remove_course_response.status_code == 204
    assert remove_course_response.content == b""

    removed_course_response = await client.get(f"/api/courses/{course_id}")
    assert removed_course_response.status_code == 404
    assert removed_course_response.json()["error"] == "course_not_found"

    removed_structure_response = await client.get(
        f"/api/courses/{course_id}/structure"
    )
    assert removed_structure_response.status_code == 404
    assert removed_structure_response.json()["error"] == "course_not_found"

    courses_response = await client.get("/api/courses")
    assert courses_response.status_code == 200
    assert [course["id"] for course in courses_response.json()] == [control_course_id]

    control_course_read_response = await client.get(
        f"/api/courses/{control_course_id}"
    )
    assert control_course_read_response.status_code == 200
