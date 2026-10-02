from app.application.interfaces.student_analytics_cache import (
    StudentAnalyticsCache,
)
from app.bootstrap.build_submission_queue import get_redis_client
from app.infrastructure.cache.redis_student_analytics_cache import (
    RedisStudentAnalyticsCache,
)
from app.infrastructure.config.settings import get_settings


def build_student_analytics_cache() -> StudentAnalyticsCache:
    settings = get_settings()
    return RedisStudentAnalyticsCache(
        client=get_redis_client(),
        ttl_seconds=settings.analytics_cache_ttl_seconds,
    )
