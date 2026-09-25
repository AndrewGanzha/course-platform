from uuid import UUID

from redis.asyncio import Redis

from app.application.interfaces.submission_queue import SubmissionQueue

_DEQUEUE_POLL_TIMEOUT_SECONDS = 1


class RedisSubmissionQueue(SubmissionQueue):
    def __init__(self, client: Redis, queue_name: str) -> None:
        self.client = client
        self.queue_name = queue_name

    async def enqueue(self, submission_id: UUID) -> None:
        await self.client.rpush(self.queue_name, str(submission_id))

    async def dequeue(self) -> UUID:
        while True:
            result = await self.client.blpop(
                self.queue_name,
                timeout=_DEQUEUE_POLL_TIMEOUT_SECONDS,
            )
            if result is not None:
                break

        _, raw_submission_id = result
        return UUID(raw_submission_id.decode("utf-8"))
