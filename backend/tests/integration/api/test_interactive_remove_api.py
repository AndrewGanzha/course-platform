from uuid import uuid4

import pytest

from app.infrastructure.database.models import (
    AnswerOptionModel,
    QuestionModel,
    SectionModel,
)


@pytest.mark.asyncio
async def test_remove_question_returns_204_and_deletes_its_options(
    client,
    author_auth_headers,
    seeded_interactive_tree,
    session_factory,
) -> None:
    response = await client.delete(
        f'/api/admin/questions/{seeded_interactive_tree.question_id}',
        headers=author_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b''

    async with session_factory() as session:
        assert (
            await session.get(QuestionModel, seeded_interactive_tree.question_id)
            is None
        )
        assert (
            await session.get(
                AnswerOptionModel,
                seeded_interactive_tree.wrong_option_id,
            )
            is None
        )
        assert (
            await session.get(
                AnswerOptionModel,
                seeded_interactive_tree.correct_option_id,
            )
            is None
        )
        assert (
            await session.get(SectionModel, seeded_interactive_tree.section_id)
            is not None
        )


@pytest.mark.asyncio
async def test_remove_answer_option_returns_204_when_question_remains_valid(
    client,
    author_auth_headers,
    seeded_interactive_tree,
    session_factory,
) -> None:
    extra_option_id = str(uuid4())
    async with session_factory() as session:
        session.add(
            AnswerOptionModel(
                id=extra_option_id,
                question_id=seeded_interactive_tree.question_id,
                text='PATCH',
                position=3,
                is_correct=False,
            )
        )
        await session.commit()

    response = await client.delete(
        f'/api/admin/answer-options/{seeded_interactive_tree.wrong_option_id}',
        headers=author_auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b''

    async with session_factory() as session:
        assert (
            await session.get(
                AnswerOptionModel,
                seeded_interactive_tree.wrong_option_id,
            )
            is None
        )
        assert (
            await session.get(
                AnswerOptionModel,
                seeded_interactive_tree.correct_option_id,
            )
            is not None
        )
        assert await session.get(AnswerOptionModel, extra_option_id) is not None
        assert (
            await session.get(QuestionModel, seeded_interactive_tree.question_id)
            is not None
        )


@pytest.mark.asyncio
async def test_remove_answer_option_rejects_invalid_question_configuration(
    client,
    author_auth_headers,
    seeded_interactive_tree,
    session_factory,
) -> None:
    response = await client.delete(
        f'/api/admin/answer-options/{seeded_interactive_tree.wrong_option_id}',
        headers=author_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'domain_error'

    async with session_factory() as session:
        assert (
            await session.get(
                AnswerOptionModel,
                seeded_interactive_tree.wrong_option_id,
            )
            is not None
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('resource', 'id_attribute', 'model_type'),
    [
        ('questions', 'question_id', QuestionModel),
        ('answer-options', 'wrong_option_id', AnswerOptionModel),
    ],
)
async def test_remove_interactive_content_rejects_used_question(
    client,
    student_auth_headers,
    author_auth_headers,
    seeded_interactive_tree,
    session_factory,
    resource,
    id_attribute,
    model_type,
) -> None:
    attempt_response = await client.post(
        f'/api/learning/questions/{seeded_interactive_tree.question_id}/attempts',
        headers=student_auth_headers,
        json={
            'selected_option_ids': [seeded_interactive_tree.wrong_option_id],
        },
    )
    assert attempt_response.status_code == 201

    resource_id = getattr(seeded_interactive_tree, id_attribute)
    response = await client.delete(
        f'/api/admin/{resource}/{resource_id}',
        headers=author_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()['error'] == 'application_error'

    async with session_factory() as session:
        assert await session.get(model_type, resource_id) is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('resource', 'id_attribute'),
    [
        ('questions', 'question_id'),
        ('answer-options', 'wrong_option_id'),
    ],
)
async def test_foreign_author_cannot_remove_interactive_content(
    client,
    other_author_auth_headers,
    seeded_interactive_tree,
    resource,
    id_attribute,
) -> None:
    resource_id = getattr(seeded_interactive_tree, id_attribute)
    response = await client.delete(
        f'/api/admin/{resource}/{resource_id}',
        headers=other_author_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()['error'] == 'permission_denied'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('resource', 'error'),
    [
        ('questions', 'question_not_found'),
        ('answer-options', 'answer_option_not_found'),
    ],
)
async def test_remove_missing_interactive_content_returns_404(
    client,
    author_auth_headers,
    resource,
    error,
) -> None:
    response = await client.delete(
        f'/api/admin/{resource}/{uuid4()}',
        headers=author_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()['error'] == error


@pytest.mark.asyncio
@pytest.mark.parametrize('resource', ['questions', 'answer-options'])
async def test_remove_interactive_content_requires_authentication(
    client,
    resource,
) -> None:
    response = await client.delete(f'/api/admin/{resource}/{uuid4()}')

    assert response.status_code == 401
    assert response.json()['error'] == 'authentication_error'
