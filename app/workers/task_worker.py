import asyncio

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.queue.task_queue import dequeue_task
from app.services.task_service import (
    get_task,
    mark_task_completed,
    mark_task_failed,
    mark_task_running,
)


async def execute_task(task_id: int):

    db: Session = SessionLocal()

    try:

        task = db.query(
            __import__(
                "app.models.task",
                fromlist=["Task"],
            ).Task
        ).filter(
            __import__(
                "app.models.task",
                fromlist=["Task"],
            ).Task.id == task_id
        ).first()

        if task is None:
            return

        mark_task_running(
            db,
            task,
        )

        await asyncio.sleep(2)

        result = {
            "message": "Task executed successfully",
            "task_id": task.id,
            "agent_id": task.agent_id,
            "task_type": task.task_type,
            "input_received": task.input_data,
        }

        mark_task_completed(
            db,
            task,
            result,
        )

    except Exception as exc:

        task = get_task(
            db,
            task_id,
            owner_id=task.owner_id if "task" in locals() and task else 0,
        )

        if task:
            mark_task_failed(
                db,
                task,
                str(exc),
            )

    finally:
        db.close()


async def worker_loop():

    print("AgentMesh Task Worker started")

    while True:

        task_payload = await dequeue_task()

        if task_payload is None:
            await asyncio.sleep(1)
            continue

        task_id = task_payload["task_id"]

        print(
            f"Executing task {task_id}"
        )

        await execute_task(
            task_id
        )


if __name__ == "__main__":
    asyncio.run(
        worker_loop()
    )