from functools import lru_cache

from app.application.interfaces.content_cache import ContentCache
from app.bootstrap.build_submission_queue import get_redis_client
from app.infrastructure.cache.redis_content_cache import RedisContentCache
from app.infrastructure.config.settings import get_settings


@lru_cache(maxsize=1)
def build_content_cache() -> ContentCache:
    settings = get_settings()
    return RedisContentCache(
        client=get_redis_client(),
        ttl_seconds=settings.content_cache_ttl_seconds,
    )
