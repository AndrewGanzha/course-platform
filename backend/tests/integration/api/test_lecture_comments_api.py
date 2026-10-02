import pytest


async def _create_comment(client, headers, lecture_id, text="First comment"):
    return await client.post(
        f"/api/lectures/{lecture_id}/comments",
        headers=headers,
        json={"text": text},
    )


@pytest.mark.asyncio
async def test_student_can_list_comments_of_available_lecture(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    response = await client.get(
        f"/api/lectures/{seeded_interactive_tree.lecture_id}/comments"
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_student_can_create_comment_on_available_lecture(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    response = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "Really helpful lecture.",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["lecture_id"] == seeded_interactive_tree.lecture_id
    assert payload["text"] == "Really helpful lecture."
    assert payload["updated_at"] is None


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_create_comment(
    client,
    seeded_interactive_tree,
):
    response = await client.post(
        f"/api/lectures/{seeded_interactive_tree.lecture_id}/comments",
        json={"text": "Anonymous comment."},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_student_cannot_comment_on_unavailable_lecture(
    client,
    student_auth_headers,
    seeded_draft_lecture_tree,
):
    response = await _create_comment(
        client,
        student_auth_headers,
        seeded_draft_lecture_tree.lecture_id,
        "Should not be allowed.",
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_comment_author_can_update_comment(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    created = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "Initial text.",
    )
    comment_id = created.json()["id"]

    response = await client.patch(
        f"/api/comments/{comment_id}",
        headers=student_auth_headers,
        json={"text": "Updated text."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == comment_id
    assert payload["text"] == "Updated text."
    assert payload["updated_at"] is not None


@pytest.mark.asyncio
async def test_other_student_cannot_update_foreign_comment(
    client,
    student_auth_headers,
    seeded_interactive_tree,
    seeded_author_analytics_tree,
):
    created = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "Owned by first student.",
    )
    comment_id = created.json()["id"]

    # The second student is registered via the analytics fixture user.
    login = await client.post(
        "/api/auth/login",
        json={
            "email": "analytics-student@example.com",
            "password": "strongpassword123",
        },
    )
    other_headers = {
        "Authorization": f"Bearer {login.json()['access_token']}",
    }

    response = await client.patch(
        f"/api/comments/{comment_id}",
        headers=other_headers,
        json={"text": "Hijacked text."},
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_comment_author_can_delete_own_comment(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    created = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "To be removed.",
    )
    comment_id = created.json()["id"]

    response = await client.delete(
        f"/api/comments/{comment_id}",
        headers=student_auth_headers,
    )

    assert response.status_code == 204
    listing = await client.get(
        f"/api/lectures/{seeded_interactive_tree.lecture_id}/comments"
    )
    assert listing.json() == []


@pytest.mark.asyncio
async def test_course_author_can_delete_comment_of_own_course(
    client,
    student_auth_headers,
    author_auth_headers,
    seeded_interactive_tree,
):
    created = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "Moderated by course author.",
    )
    comment_id = created.json()["id"]

    response = await client.delete(
        f"/api/comments/{comment_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_other_author_cannot_delete_comment(
    client,
    student_auth_headers,
    other_author_auth_headers,
    seeded_interactive_tree,
):
    created = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "Foreign author must not touch this.",
    )
    comment_id = created.json()["id"]

    response = await client.delete(
        f"/api/comments/{comment_id}",
        headers=other_author_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_can_delete_any_comment(
    client,
    student_auth_headers,
    admin_auth_headers,
    seeded_interactive_tree,
):
    created = await _create_comment(
        client,
        student_auth_headers,
        seeded_interactive_tree.lecture_id,
        "Comment moderated by admin.",
    )
    comment_id = created.json()["id"]

    response = await client.delete(
        f"/api/comments/{comment_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_comments_are_returned_in_creation_order(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    lecture_id = seeded_interactive_tree.lecture_id
    for text in ("First", "Second", "Third"):
        await _create_comment(client, student_auth_headers, lecture_id, text)

    response = await client.get(f"/api/lectures/{lecture_id}/comments")

    assert response.status_code == 200
    assert [comment["text"] for comment in response.json()] == [
        "First",
        "Second",
        "Third",
    ]


@pytest.mark.asyncio
async def test_missing_comment_returns_404(
    client,
    student_auth_headers,
):
    from uuid import uuid4

    response = await client.patch(
        f"/api/comments/{uuid4()}",
        headers=student_auth_headers,
        json={"text": "Ghost comment."},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "lecture_comment_not_found"
