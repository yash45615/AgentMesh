import asyncio
import time
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

# IMPORTANT:
# Register every SQLAlchemy model before any ORM query runs.
from app.db import models

from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.task import Task
from app.queue.task_queue import (
    dequeue_task,
    enqueue_task,
)
from app.runtime.agent_runtime import AgentRuntime
from app.services.task_service import (
    mark_task_completed,
    mark_task_failed,
    mark_task_running,
    retry_task,
)
from app.observability.metrics import metrics


class Worker:

    def __init__(self):

        self.worker_id = str(
            uuid.uuid4()
        )

        self.running = True

        self.runtime = AgentRuntime()

        metrics.worker_started_event()

    async def execute_task(
        self,
        db: Session,
        task: Task,
    ) -> dict:

        agent = db.execute(
            select(Agent).where(
                Agent.id == task.agent_id,
                Agent.is_active.is_(True),
                Agent.owner_id == task.owner_id,
            )
        ).scalar_one_or_none()

        if agent is None:

            raise ValueError(
                f"Agent {task.agent_id} "
                f"not found, inactive, "
                f"or ownership mismatch."
            )

        print(
            f"[Worker {self.worker_id}] "
            f"Selected agent "
            f"{agent.id} "
            f"({agent.name})"
        )

        result = await asyncio.wait_for(
            self.runtime.execute(
                agent=agent,
                task=task,
            ),
            timeout=task.timeout_seconds,
        )

        return result

    async def process_task(
        self,
        task_id: str,
    ) -> None:

        db: Session = SessionLocal()

        try:

            task = db.get(
                Task,
                int(task_id),
            )

            if task is None:

                print(
                    f"[Worker {self.worker_id}] "
                    f"Task {task_id} not found."
                )

                return

            if task.status != "queued":

                print(
                    f"[Worker {self.worker_id}] "
                    f"Task {task_id} ignored. "
                    f"Status={task.status}"
                )

                return

            mark_task_running(
                db=db,
                task=task,
            )

            print(
                f"[Worker {self.worker_id}] "
                f"Task {task.id} "
                f"status=RUNNING"
            )

            task_start_time = (
                time.perf_counter()
            )

            try:

                result = await self.execute_task(
                    db=db,
                    task=task,
                )

                duration = (
                    time.perf_counter()
                    - task_start_time
                )

                mark_task_completed(
                    db=db,
                    task=task,
                    result=result,
                )

                metrics.task_completed(
                    duration=duration
                )

                print(
                    f"[Worker {self.worker_id}] "
                    f"Task {task.id} "
                    f"status=COMPLETED "
                    f"duration="
                    f"{duration:.2f}s"
                )

            except asyncio.TimeoutError:

                metrics.task_timed_out()

                error_message = (
                    "Task execution timed out "
                    f"after "
                    f"{task.timeout_seconds} "
                    "seconds."
                )

                print(
                    f"[Worker {self.worker_id}] "
                    f"Task {task.id} "
                    f"TIMEOUT"
                )

                if (
                    task.retry_count
                    < task.max_retries
                ):

                    retry_task(
                        db=db,
                        task=task,
                    )

                    metrics.task_retried()

                    await enqueue_task(
                        task_id=task.id,
                        priority=task.priority,
                    )

                    print(
                        f"[Worker {self.worker_id}] "
                        f"Task {task.id} "
                        f"queued for retry "
                        f"("
                        f"{task.retry_count}/"
                        f"{task.max_retries}"
                        f")"
                    )

                else:

                    mark_task_failed(
                        db=db,
                        task=task,
                        error_message=error_message,
                    )

                    metrics.task_failed()

                    print(
                        f"[Worker {self.worker_id}] "
                        f"Task {task.id} "
                        f"status=FAILED"
                    )

            except Exception as exc:

                error_message = str(exc)

                metrics.error(
                    type(exc).__name__
                )

                print(
                    f"[Worker {self.worker_id}] "
                    f"Task {task.id} "
                    f"execution failed: "
                    f"{error_message}"
                )

                if (
                    task.retry_count
                    < task.max_retries
                ):

                    retry_task(
                        db=db,
                        task=task,
                    )

                    metrics.task_retried()

                    await enqueue_task(
                        task_id=task.id,
                        priority=task.priority,
                    )

                    print(
                        f"[Worker {self.worker_id}] "
                        f"Task {task.id} "
                        f"queued for retry "
                        f"("
                        f"{task.retry_count}/"
                        f"{task.max_retries}"
                        f")"
                    )

                else:

                    mark_task_failed(
                        db=db,
                        task=task,
                        error_message=error_message,
                    )

                    metrics.task_failed()

                    print(
                        f"[Worker {self.worker_id}] "
                        f"Task {task.id} "
                        f"status=FAILED"
                    )

        finally:

            db.close()

    async def heartbeat(self):

        while self.running:

            print(
                f"[Heartbeat] "
                f"Worker "
                f"{self.worker_id} "
                f"alive"
            )

            await asyncio.sleep(10)

    async def run(self):

        print(
            f"Worker "
            f"{self.worker_id} "
            f"started."
        )

        heartbeat_task = (
            asyncio.create_task(
                self.heartbeat()
            )
        )

        try:

            while self.running:

                task_id = (
                    await dequeue_task()
                )

                if task_id is None:

                    continue

                print(
                    f"[Worker "
                    f"{self.worker_id}] "
                    f"Received task "
                    f"{task_id}"
                )

                await self.process_task(
                    task_id
                )

        except asyncio.CancelledError:

            print(
                f"Worker "
                f"{self.worker_id} "
                f"stopping."
            )

        finally:

            self.running = False

            heartbeat_task.cancel()

            try:

                await heartbeat_task

            except asyncio.CancelledError:

                pass

            print(
                f"Worker "
                f"{self.worker_id} "
                f"stopped."
            )


async def main():

    worker = Worker()

    try:

        await worker.run()

    except KeyboardInterrupt:

        worker.running = False

        print(
            f"Worker "
            f"{worker.worker_id} "
            f"interrupted."
        )


if __name__ == "__main__":

    asyncio.run(main())