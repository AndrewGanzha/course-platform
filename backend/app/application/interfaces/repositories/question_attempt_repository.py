from abc import ABC, abstractmethod
from uuid import UUID


class QuestionAttemptRepository(ABC):
    @abstractmethod
    async def exists_by_question_id(self, question_id: UUID) -> bool:
        raise NotImplementedError