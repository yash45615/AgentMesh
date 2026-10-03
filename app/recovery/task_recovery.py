import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db import models
from app.db.database import SessionLocal
from app.models.task import Task
from app.queue.task_queue import enqueue_task
from app.services.task_service import retry_task


class TaskRecoveryService:

    def __init__(
        self,
        stale_after_seconds: int = 60,
        scan_interval_seconds: int = 15,
    ):
        self.stale_after_seconds = stale_after_seconds
        self.scan_interval_seconds = scan_interval_seconds
        self.running = True

    async def recover_stale_tasks(self) -> int:

        db = SessionLocal()

        recovered_count = 0

        try:

            cutoff_time = (
                datetime.utcnow()
                - timedelta(
                    seconds=self.stale_after_seconds
                )
            )

            statement = select(Task).where(
                Task.status == "running",
                Task.started_at.is_not(None),
                Task.started_at < cutoff_time,
            )

            stale_tasks = list(
                db.execute(statement)
                .scalars()
                .all()
            )

            for task in stale_tasks:

                print(
                    f"[Recovery] "
                    f"Found stale task {task.id}"
                )

                if task.retry_count < task.max_retries:

                    retry_task(
                        db=db,
                        task=task,
                    )

                    await enqueue_task(
                        task_id=task.id,
                        priority=task.priority,
                    )

                    print(
                        f"[Recovery] "
                        f"Task {task.id} "
                        f"requeued successfully"
                    )

                    recovered_count += 1

                else:

                    task.status = "failed"

                    task.error_message = (
                        "Task abandoned after worker "
                        "failure and retry limit reached."
                    )

                    task.completed_at = datetime.utcnow()

                    db.commit()

                    print(
                        f"[Recovery] "
                        f"Task {task.id} "
                        f"permanently FAILED"
                    )

            return recovered_count

        finally:

            db.close()

    async def run(self):

        print(
            "[Recovery] "
            "Task recovery service started."
        )

        print(
            f"[Recovery] "
            f"Stale threshold: "
            f"{self.stale_after_seconds}s"
        )

        print(
            f"[Recovery] "
            f"Scan interval: "
            f"{self.scan_interval_seconds}s"
        )

        while self.running:

            try:

                recovered = (
                    await self.recover_stale_tasks()
                )

                if recovered > 0:

                    print(
                        f"[Recovery] "
                        f"Recovered "
                        f"{recovered} task(s)"
                    )

            except Exception as exc:

                print(
                    f"[Recovery] "
                    f"Recovery error: {exc}"
                )

            await asyncio.sleep(
                self.scan_interval_seconds
            )

    def stop(self):

        self.running = False


async def main():

    recovery_service = TaskRecoveryService()

    try:

        await recovery_service.run()

    except KeyboardInterrupt:

        recovery_service.stop()

        print(
            "[Recovery] "
            "Recovery service stopped."
        )


if __name__ == "__main__":
    asyncio.run(main())