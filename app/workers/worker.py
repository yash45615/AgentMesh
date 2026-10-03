import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.task import Task
from app.queue.task_queue import dequeue_task
from app.runtime.agent_runtime import AgentRuntime
from app.services.task_service import (
    mark_task_completed,
    mark_task_failed,
    mark_task_running,
    retry_task,
)


class Worker:

    def __init__(self):
        self.worker_id = str(uuid.uuid4())
        self.running = True
        self.runtime = AgentRuntime()

    async def execute_task(
        self,
        db: Session,
        task: Task,
    ) -> dict:

        agent = db.execute(
            select(Agent).where(
                Agent.id == task.agent_id,
                Agent.is_active.is_(True),
            )
        ).scalar_one_or_none()

        if agent is None:
            raise ValueError(
                f"Agent {task.agent_id} "
                f"not found or inactive"
            )

        print(
            f"Worker {self.worker_id} "
            f"selected agent "
            f"{agent.id} ({agent.name})"
        )

        result = await self.runtime.execute(
            agent=agent,
            task=task,
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
                    f"Task {task_id} not found."
                )
                return

            if task.status != "queued":
                print(
                    f"Task {task_id} ignored. "
                    f"Status={task.status}"
                )
                return

            mark_task_running(
                db=db,
                task=task,
            )

            print(
                f"Task {task.id} "
                f"status=RUNNING"
            )

            try:

                result = await self.execute_task(
                    db=db,
                    task=task,
                )

                mark_task_completed(
                    db=db,
                    task=task,
                    result=result,
                )

                print(
                    f"Task {task.id} "
                    f"status=COMPLETED"
                )

            except Exception as exc:

                print(
                    f"Task {task.id} "
                    f"execution failed: {exc}"
                )

                if task.retry_count < task.max_retries:

                    retry_task(
                        db=db,
                        task=task,
                    )

                    print(
                        f"Task {task.id} "
                        f"queued for retry."
                    )

                else:

                    mark_task_failed(
                        db=db,
                        task=task,
                        error_message=str(exc),
                    )

                    print(
                        f"Task {task.id} "
                        f"status=FAILED"
                    )

        finally:

            db.close()

    async def run(self):

        print(
            f"Worker {self.worker_id} started."
        )

        while self.running:

            try:

                task_id = await dequeue_task()

                if task_id is None:
                    continue

                await self.process_task(
                    task_id
                )

            except asyncio.CancelledError:

                print(
                    f"Worker "
                    f"{self.worker_id} stopping."
                )

                break

            except Exception as exc:

                print(
                    f"Worker "
                    f"{self.worker_id} error: "
                    f"{exc}"
                )

                await asyncio.sleep(2)


async def main():

    worker = Worker()

    try:
        await worker.run()

    except KeyboardInterrupt:

        print(
            f"Worker "
            f"{worker.worker_id} interrupted."
        )


if __name__ == "__main__":
    asyncio.run(main())