from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.lecture_comment_repository import (
    LectureCommentRepository,
)
from app.domain.entities.lecture_comment import LectureComment
from app.infrastructure.database.mappers.lecture_comment_mapper import (
    LectureCommentMapper,
)
from app.infrastructure.database.models.lecture_comment_model import LectureCommentModel


class SqlAlchemyLectureCommentRepository(LectureCommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, comment_id: UUID) -> LectureComment | None:
        model = await self.session.get(LectureCommentModel, str(comment_id))
        return None if model is None else LectureCommentMapper.to_domain(model)

    async def list_by_lecture_id(self, lecture_id: UUID) -> list[LectureComment]:
        stmt = (
            select(LectureCommentModel)
            .where(LectureCommentModel.lecture_id == str(lecture_id))
            .order_by(LectureCommentModel.created_at, LectureCommentModel.id)
        )
        result = await self.session.execute(stmt)
        return [
            LectureCommentMapper.to_domain(model) for model in result.scalars().all()
        ]

    async def add(self, comment: LectureComment) -> None:
        self.session.add(LectureCommentMapper.to_model(comment))
        await self.session.flush()

    async def update(self, comment: LectureComment) -> None:
        model = await self.session.get(LectureCommentModel, str(comment.id))
        if model is None:
            return
        model.text = comment.text
        model.updated_at = comment.updated_at
        await self.session.flush()

    async def delete(self, comment_id: UUID) -> None:
        model = await self.session.get(LectureCommentModel, str(comment_id))
        if model is None:
            return
        await self.session.delete(model)
        await self.session.flush()
