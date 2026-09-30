import pytest


@pytest.mark.asyncio
async def test_get_my_profile_requires_authentication(client):
    response = await client.get("/api/profile/me")

    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"


@pytest.mark.asyncio
async def test_get_my_profile_returns_current_user(client, student_auth_headers):
    response = await client.get("/api/profile/me", headers=student_auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "student@example.com"
    assert payload["role"] == "student"
    assert payload["full_name"] == ""
    assert payload["bio"] == ""
    assert payload["avatar_url"] is None


@pytest.mark.asyncio
async def test_update_my_profile_persists_changes(client, student_auth_headers):
    response = await client.patch(
        "/api/profile/me",
        headers=student_auth_headers,
        json={
            "full_name": "Jane Student",
            "bio": "Learning FastAPI.",
            "avatar_url": "https://example.com/avatar.png",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Jane Student"
    assert payload["bio"] == "Learning FastAPI."
    assert payload["avatar_url"] == "https://example.com/avatar.png"

    refreshed = await client.get("/api/profile/me", headers=student_auth_headers)
    assert refreshed.status_code == 200
    assert refreshed.json()["full_name"] == "Jane Student"


@pytest.mark.asyncio
async def test_update_my_profile_rejects_too_long_full_name(
    client,
    student_auth_headers,
):
    response = await client.patch(
        "/api/profile/me",
        headers=student_auth_headers,
        json={"full_name": "a" * 121},
    )

    assert response.status_code == 422
