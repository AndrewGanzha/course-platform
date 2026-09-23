import logging

from app.application.interfaces.submission_queue import SubmissionQueue
from app.application.use_cases.code_submissions.process_code_submission import (
    ProcessCodeSubmissionCommand,
    ProcessCodeSubmissionUseCase,
)

logger = logging.getLogger(__name__)


class CodeSubmissionWorker:
    def __init__(
        self,
        queue: SubmissionQueue,
        process_use_case: ProcessCodeSubmissionUseCase,
    ) -> None:
        self.queue = queue
        self.process_use_case = process_use_case

    async def run_forever(self) -> None:
        while True:
            submission_id = await self.queue.dequeue()

            try:
                await self.process_use_case.execute(
                    ProcessCodeSubmissionCommand(submission_id=submission_id)
                )
            except Exception:
                logger.exception(
                    "Code submission processing failed",
                    extra={"submission_id": str(submission_id)},
                )
