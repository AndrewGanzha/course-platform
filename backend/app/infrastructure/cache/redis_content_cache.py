import pickle
from uuid import UUID

from redis.asyncio import Redis

from app.application.dto.course_catalog import (
    CourseCatalogCardDTO,
    CourseCatalogItemDTO,
)
from app.application.dto.course_structure import CourseStructureDTO
from app.application.interfaces.content_cache import ContentCache


class RedisContentCache(ContentCache):
    def __init__(
        self,
        client: Redis,
        ttl_seconds: int,
    ) -> None:
        self.client = client
        self.ttl_seconds = ttl_seconds

    def _catalog_key(self, key: str) -> str:
        return f"content:catalog:{key}"

    def _course_card_key(self, course_id: UUID) -> str:
        return f"content:course:{course_id}:card"

    def _course_structure_key(self, course_id: UUID) -> str:
        return f"content:course:{course_id}:structure"

    def _dump(self, value: object) -> bytes:
        return pickle.dumps(value)

    def _load(self, value: bytes):
        return pickle.loads(value)

    async def get_catalog(
        self,
        key: str,
    ) -> list[CourseCatalogItemDTO] | None:
        value = await self.client.get(self._catalog_key(key))
        if value is None:
            return None
        return self._load(value)

    async def set_catalog(
        self,
        key: str,
        value: list[CourseCatalogItemDTO],
    ) -> None:
        await self.client.set(
            self._catalog_key(key),
            self._dump(value),
            ex=self.ttl_seconds,
        )

    async def get_course_card(
        self,
        course_id: UUID,
    ) -> CourseCatalogCardDTO | None:
        value = await self.client.get(self._course_card_key(course_id))
        if value is None:
            return None
        return self._load(value)

    async def set_course_card(
        self,
        course_id: UUID,
        value: CourseCatalogCardDTO,
    ) -> None:
        await self.client.set(
            self._course_card_key(course_id),
            self._dump(value),
            ex=self.ttl_seconds,
        )

    async def get_course_structure(
        self,
        course_id: UUID,
    ) -> CourseStructureDTO | None:
        value = await self.client.get(self._course_structure_key(course_id))
        if value is None:
            return None
        return self._load(value)

    async def set_course_structure(
        self,
        course_id: UUID,
        value: CourseStructureDTO,
    ) -> None:
        await self.client.set(
            self._course_structure_key(course_id),
            self._dump(value),
            ex=self.ttl_seconds,
        )

    async def invalidate_course(
        self,
        course_id: UUID,
    ) -> None:
        keys = [
            self._course_card_key(course_id),
            self._course_structure_key(course_id),
        ]

        async for key in self.client.scan_iter(match="content:catalog:*"):
            keys.append(key)

        if keys:
            await self.client.delete(*keys)
