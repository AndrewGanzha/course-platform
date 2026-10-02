from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.entities.lecture_comment import MAX_COMMENT_LENGTH, LectureComment
from app.domain.exceptions import InvalidLectureCommentError


def _make_comment(text: str = "Useful lecture") -> LectureComment:
    return LectureComment(
        id=uuid4(),
        lecture_id=uuid4(),
        user_id=uuid4(),
        text=text,
        created_at=datetime.now(UTC),
    )


def test_lecture_comment_is_created_with_valid_data() -> None:
    comment = _make_comment("Great explanation")

    assert comment.text == "Great explanation"
    assert comment.updated_at is None


def test_lecture_comment_rejects_empty_text() -> None:
    with pytest.raises(InvalidLectureCommentError):
        _make_comment("   ")


def test_lecture_comment_rejects_too_long_text() -> None:
    with pytest.raises(InvalidLectureCommentError):
        _make_comment("x" * (MAX_COMMENT_LENGTH + 1))


def test_lecture_comment_strips_surrounding_whitespace() -> None:
    comment = _make_comment("  trimmed  ")

    assert comment.text == "trimmed"


def test_lecture_comment_update_changes_text_and_updated_at() -> None:
    comment = _make_comment("Before")
    assert comment.updated_at is None

    comment.update(text="  After  ")

    assert comment.text == "After"
    assert comment.updated_at is not None
