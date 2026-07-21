from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.module import Module


class ModuleRepository(ABC):
    @abstractmethod
    async def get_by_ids(self, module_ids: list[UUID]) -> list[Module]:
        raise NotImplementedError