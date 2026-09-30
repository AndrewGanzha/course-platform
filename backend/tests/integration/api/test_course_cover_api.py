from pathlib import Path
from uuid import uuid4

import pytest

PNG_BYTES = b"\x89PNG\r\n\x1a\ncover-image-payload"
WEBP_BYTES = b"RIFF....WEBPcover-image-payload"
MAX_COVER_IMAGE_BYTES = 1024 * 1024


def image_part(
    filename: str,
    content: bytes = PNG_BYTES,
    content_type: str = "image/png",
) -> dict:
    return {"file": (filename, content, content_type)}


async def create_course(client, headers) -> str:
    response = await client.post(
        "/api/admin/courses",
        headers=headers,
        json={"title": "Cover course", "description": "Cover upload course."},
    )
    assert response.status_code == 201
    return response.json()["id"]


async def make_course_publishable(client, headers, course_id: str) -> None:
    module_response = await client.post(
        f"/api/admin/courses/{course_id}/modules",
        headers=headers,
        json={"title": "Module", "description": "Module.", "position": 1},
    )
    module_id = module_response.json()["id"]

    section_response = await client.post(
        f"/api/admin/modules/{module_id}/sections",
        headers=headers,
        json={"title": "Section", "description": "Section.", "position": 1},
    )
    section_id = section_response.json()["id"]

    await client.post(
        f"/api/admin/sections/{section_id}/lectures",
        headers=headers,
        json={"title": "Lecture", "content": "Content.", "position": 1},
    )


@pytest.mark.asyncio
async def test_owner_can_upload_cover_and_the_file_is_served(
    client,
    author_auth_headers,
    media_root: Path,
):
    course_id = await create_course(client, author_auth_headers)

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files=image_part("cover.png"),
    )

    assert response.status_code == 200
    cover_url = response.json()["cover_image_url"]
    assert cover_url is not None
    assert cover_url.startswith("/media/course-covers/")
    assert cover_url.endswith(".png")

    stored_file = media_root / cover_url.removeprefix("/media/")
    assert stored_file.is_file()
    assert stored_file.read_bytes() == PNG_BYTES

    served = await client.get(cover_url)
    assert served.status_code == 200
    assert served.content == PNG_BYTES


@pytest.mark.asyncio
async def test_admin_can_upload_cover_for_any_course(
    client,
    admin_auth_headers,
    seeded_course_tree,
):
    response = await client.post(
        f"/api/admin/courses/{seeded_course_tree.course_id}/cover",
        headers=admin_auth_headers,
        files=image_part(
            "cover.webp",
            content=WEBP_BYTES,
            content_type="image/webp",
        ),
    )

    assert response.status_code == 200
    assert response.json()["cover_image_url"].endswith(".webp")


@pytest.mark.asyncio
async def test_other_author_cannot_upload_cover(
    client,
    other_author_auth_headers,
    seeded_course_tree,
):
    response = await client.post(
        f"/api/admin/courses/{seeded_course_tree.course_id}/cover",
        headers=other_author_auth_headers,
        files=image_part("cover.png"),
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_student_cannot_upload_cover(
    client,
    student_auth_headers,
    seeded_course_tree,
):
    response = await client.post(
        f"/api/admin/courses/{seeded_course_tree.course_id}/cover",
        headers=student_auth_headers,
        files=image_part("cover.png"),
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_anonymous_cannot_upload_cover(client, seeded_course_tree):
    response = await client.post(
        f"/api/admin/courses/{seeded_course_tree.course_id}/cover",
        files=image_part("cover.png"),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_rejects_unknown_course(client, author_auth_headers):
    response = await client.post(
        f"/api/admin/courses/{uuid4()}/cover",
        headers=author_auth_headers,
        files=image_part("cover.png"),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_upload_rejects_non_image_file(client, author_auth_headers):
    course_id = await create_course(client, author_auth_headers)

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("notes.txt", b"just text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_cover_image"


@pytest.mark.asyncio
async def test_upload_rejects_content_type_extension_mismatch(
    client,
    author_auth_headers,
):
    course_id = await create_course(client, author_auth_headers)

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files=image_part(
            "cover.png",
            content=PNG_BYTES,
            content_type="text/plain",
        ),
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_cover_image"


@pytest.mark.asyncio
async def test_upload_rejects_oversized_image(client, author_auth_headers):
    course_id = await create_course(client, author_auth_headers)
    oversized = b"x" * (MAX_COVER_IMAGE_BYTES + 1)

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files=image_part("big.png", content=oversized),
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_cover_image"


@pytest.mark.asyncio
async def test_uploaded_cover_reaches_public_catalog_after_publish(
    client,
    author_auth_headers,
):
    course_id = await create_course(client, author_auth_headers)

    upload_response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files=image_part("cover.png"),
    )
    cover_url = upload_response.json()["cover_image_url"]

    await make_course_publishable(client, author_auth_headers, course_id)
    publish_response = await client.post(
        f"/api/admin/courses/{course_id}/publish",
        headers=author_auth_headers,
    )
    assert publish_response.status_code == 200

    card_response = await client.get(f"/api/courses/{course_id}")
    assert card_response.status_code == 200
    assert card_response.json()["cover_image_url"] == cover_url

    catalog_response = await client.get("/api/courses")
    assert catalog_response.status_code == 200
    catalog_item = next(
        item for item in catalog_response.json() if item["id"] == course_id
    )
    assert catalog_item["cover_image_url"] == cover_url
