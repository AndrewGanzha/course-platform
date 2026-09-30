from uuid import UUID

from app.domain.entities.course import Course, CourseDifficulty, CourseStatus
from app.infrastructure.database.models.course_model import CourseModel


class CourseMapper:
    @staticmethod
    def to_domain(model: CourseModel) -> Course:
        return Course(
            id=UUID(model.id),
            author_id=UUID(model.author_id),
            title=model.title,
            description=model.description,
            status=CourseStatus(model.status),
            cover_image_url=model.cover_image_url,
            short_description=model.short_description,
            difficulty=CourseDifficulty(model.difficulty),
            tag_names=list(model.tag_names or []),
            module_ids=[
                UUID(module.id)
                for module in sorted(model.modules, key=lambda x: x.position)
            ],
        )

    @staticmethod
    def to_model(entity: Course) -> CourseModel:
        return CourseModel(
            id=str(entity.id),
            author_id=str(entity.author_id),
            title=entity.title,
            description=entity.description,
            status=str(entity.status),
            cover_image_url=entity.cover_image_url,
            short_description=entity.short_description,
            difficulty=str(entity.difficulty),
            tag_names=list(entity.tag_names),
        )
