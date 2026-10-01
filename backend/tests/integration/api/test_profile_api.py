import pytest


@pytest.mark.asyncio
async def test_get_my_profile_returns_authenticated_user_profile(
    client,
    student_auth_headers,
):
    response = await client.get("/api/profile/me", headers=student_auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "student@example.com"
    assert payload["role"] == "student"
    assert payload["full_name"] == ""
    assert payload["bio"] == ""
    assert payload["avatar_url"] is None


@pytest.mark.asyncio
async def test_update_my_profile_changes_profile_fields(
    client,
    student_auth_headers,
):
    response = await client.patch(
        "/api/profile/me",
        headers=student_auth_headers,
        json={
            "full_name": "Ivan Petrov",
            "bio": "Learning backend development.",
            "avatar_url": "https://example.com/avatars/ivan.png",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Ivan Petrov"
    assert payload["bio"] == "Learning backend development."
    assert payload["avatar_url"] == "https://example.com/avatars/ivan.png"


@pytest.mark.asyncio
async def test_get_my_profile_returns_updated_profile_data(
    client,
    student_auth_headers,
):
    await client.patch(
        "/api/profile/me",
        headers=student_auth_headers,
        json={
            "full_name": "Ivan Petrov",
            "bio": "Learning backend development.",
            "avatar_url": "https://example.com/avatars/ivan.png",
        },
    )

    response = await client.get("/api/profile/me", headers=student_auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Ivan Petrov"
    assert payload["bio"] == "Learning backend development."
    assert payload["avatar_url"] == "https://example.com/avatars/ivan.png"
