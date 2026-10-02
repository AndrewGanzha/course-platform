import pytest


@pytest.mark.asyncio
async def test_student_can_create_review_at_eighty_percent(
    client,
    student_auth_headers,
    seeded_review_eligibility,
):
    response = await client.put(
        f"/api/courses/{seeded_review_eligibility.eligible_course_id}/reviews/me",
        headers=student_auth_headers,
        json={
            "rating": 5,
            "text": "Strong practical course.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["course_id"] == seeded_review_eligibility.eligible_course_id
    assert payload["rating"] == 5
    assert payload["text"] == "Strong practical course."


@pytest.mark.asyncio
async def test_student_cannot_create_review_below_eighty_percent(
    client,
    student_auth_headers,
    seeded_review_eligibility,
):
    response = await client.put(
        f"/api/courses/{seeded_review_eligibility.ineligible_course_id}/reviews/me",
        headers=student_auth_headers,
        json={
            "rating": 5,
            "text": "Not enough progress yet.",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_student_cannot_review_course_without_progress(
    client,
    student_auth_headers,
    seeded_course_tree,
):
    response = await client.put(
        f"/api/courses/{seeded_course_tree.course_id}/reviews/me",
        headers=student_auth_headers,
        json={
            "rating": 5,
            "text": "I have not started this course yet.",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_student_can_update_own_course_review(
    client,
    student_auth_headers,
    seeded_review_eligibility,
):
    course_id = seeded_review_eligibility.eligible_course_id

    first_response = await client.put(
        f"/api/courses/{course_id}/reviews/me",
        headers=student_auth_headers,
        json={"rating": 4, "text": "Good course."},
    )
    assert first_response.status_code == 200
    review_id = first_response.json()["id"]

    second_response = await client.put(
        f"/api/courses/{course_id}/reviews/me",
        headers=student_auth_headers,
        json={"rating": 5, "text": "Excellent after the update."},
    )

    assert second_response.status_code == 200
    payload = second_response.json()
    assert payload["id"] == review_id
    assert payload["rating"] == 5
    assert payload["text"] == "Excellent after the update."


@pytest.mark.asyncio
async def test_public_course_reviews_returns_created_review(
    client,
    student_auth_headers,
    seeded_review_eligibility,
):
    course_id = seeded_review_eligibility.eligible_course_id
    await client.put(
        f"/api/courses/{course_id}/reviews/me",
        headers=student_auth_headers,
        json={"rating": 5, "text": "Useful and clear."},
    )

    response = await client.get(f"/api/courses/{course_id}/reviews")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["rating"] == 5
    assert payload[0]["text"] == "Useful and clear."


@pytest.mark.asyncio
async def test_author_cannot_leave_course_review(
    client,
    author_auth_headers,
    seeded_review_eligibility,
):
    response = await client.put(
        f"/api/courses/{seeded_review_eligibility.eligible_course_id}/reviews/me",
        headers=author_auth_headers,
        json={
            "rating": 5,
            "text": "Author should not review courses as a student.",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_course_catalog_includes_rating_after_review(
    client,
    student_auth_headers,
    seeded_review_eligibility,
):
    course_id = seeded_review_eligibility.eligible_course_id
    await client.put(
        f"/api/courses/{course_id}/reviews/me",
        headers=student_auth_headers,
        json={
            "rating": 4,
            "text": "Good practical material.",
        },
    )

    response = await client.get("/api/courses")

    assert response.status_code == 200
    course = next(item for item in response.json() if item["id"] == course_id)
    assert course["rating"]["average_rating"] == 4.0
    assert course["rating"]["reviews_count"] == 1
