from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.course_catalog import (
    CourseCatalogCountersDTO,
    CourseCatalogMetricsDTO,
)
from app.application.dto.course_reviews import CourseRatingSummaryDTO
from app.application.interfaces.repositories.course_catalog_metrics_repository import (
    CourseCatalogMetricsRepository,
)
from app.infrastructure.database.models.code_task_model import CodeTaskModel
from app.infrastructure.database.models.course_review_model import CourseReviewModel
from app.infrastructure.database.models.lecture_model import LectureModel
from app.infrastructure.database.models.module_model import ModuleModel
from app.infrastructure.database.models.question_model import QuestionModel
from app.infrastructure.database.models.section_model import SectionModel
from app.infrastructure.database.models.task_model import TaskModel


class SqlAlchemyCourseCatalogMetricsRepository(CourseCatalogMetricsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _load_counts(self, stmt) -> dict[str, int]:
        result = await self.session.execute(stmt)
        return {course_id: int(count) for course_id, count in result.all()}

    async def get_by_course_ids(
        self,
        course_ids: list[UUID],
    ) -> dict[UUID, CourseCatalogMetricsDTO]:
        if not course_ids:
            return {}

        raw_course_ids = [str(course_id) for course_id in course_ids]

        module_counts = await self._load_counts(
            select(
                ModuleModel.course_id,
                func.count(ModuleModel.id),
            )
            .where(ModuleModel.course_id.in_(raw_course_ids))
            .group_by(ModuleModel.course_id)
        )

        section_counts = await self._load_counts(
            select(
                ModuleModel.course_id,
                func.count(SectionModel.id),
            )
            .join(
                SectionModel,
                SectionModel.module_id == ModuleModel.id,
            )
            .where(ModuleModel.course_id.in_(raw_course_ids))
            .group_by(ModuleModel.course_id)
        )

        lecture_counts = await self._load_counts(
            select(
                ModuleModel.course_id,
                func.count(LectureModel.id),
            )
            .join(
                SectionModel,
                SectionModel.module_id == ModuleModel.id,
            )
            .join(
                LectureModel,
                LectureModel.section_id == SectionModel.id,
            )
            .where(ModuleModel.course_id.in_(raw_course_ids))
            .group_by(ModuleModel.course_id)
        )

        question_counts = await self._load_counts(
            select(
                ModuleModel.course_id,
                func.count(QuestionModel.id),
            )
            .join(
                SectionModel,
                SectionModel.module_id == ModuleModel.id,
            )
            .join(
                QuestionModel,
                QuestionModel.section_id == SectionModel.id,
            )
            .where(ModuleModel.course_id.in_(raw_course_ids))
            .group_by(ModuleModel.course_id)
        )

        task_counts = await self._load_counts(
            select(
                ModuleModel.course_id,
                func.count(TaskModel.id),
            )
            .join(
                SectionModel,
                SectionModel.module_id == ModuleModel.id,
            )
            .join(
                TaskModel,
                TaskModel.section_id == SectionModel.id,
            )
            .where(ModuleModel.course_id.in_(raw_course_ids))
            .group_by(ModuleModel.course_id)
        )

        code_task_counts = await self._load_counts(
            select(
                ModuleModel.course_id,
                func.count(CodeTaskModel.id),
            )
            .join(
                SectionModel,
                SectionModel.module_id == ModuleModel.id,
            )
            .join(
                CodeTaskModel,
                CodeTaskModel.section_id == SectionModel.id,
            )
            .where(ModuleModel.course_id.in_(raw_course_ids))
            .group_by(ModuleModel.course_id)
        )

        rating_result = await self.session.execute(
            select(
                CourseReviewModel.course_id,
                func.count(CourseReviewModel.id),
                func.avg(CourseReviewModel.rating),
            )
            .where(CourseReviewModel.course_id.in_(raw_course_ids))
            .group_by(CourseReviewModel.course_id)
        )
        ratings = {
            course_id: (int(reviews_count), float(average_rating))
            for course_id, reviews_count, average_rating in rating_result.all()
        }

        metrics: dict[UUID, CourseCatalogMetricsDTO] = {}
        for course_id in course_ids:
            raw_course_id = str(course_id)
            reviews_count, average_rating = ratings.get(raw_course_id, (0, 0.0))

            metrics[course_id] = CourseCatalogMetricsDTO(
                counters=CourseCatalogCountersDTO(
                    module_count=module_counts.get(raw_course_id, 0),
                    section_count=section_counts.get(raw_course_id, 0),
                    lecture_count=lecture_counts.get(raw_course_id, 0),
                    question_count=question_counts.get(raw_course_id, 0),
                    task_count=task_counts.get(raw_course_id, 0),
                    code_task_count=code_task_counts.get(raw_course_id, 0),
                ),
                rating=CourseRatingSummaryDTO(
                    average_rating=average_rating,
                    reviews_count=reviews_count,
                ),
            )

        return metrics
