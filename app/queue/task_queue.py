
from __future__ import annotations

from app.core.redis import redis_client


TASK_QUEUE = "agentmesh:tasks"


def normalize_task_id(task_id) -> int:
    """
    Convert a Task ORM object or an integer/string ID into
    a valid integer task ID.

    Redis must only receive task IDs, never SQLAlchemy Task objects.
    """

    # SQLAlchemy Task object
    if hasattr(task_id, "id"):
        task_id = task_id.id

    if task_id is None:
        raise ValueError("Task ID cannot be None.")

    try:
        return int(task_id)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid task ID: {task_id!r}. "
            "Expected an integer task ID or Task object."
        ) from exc


async def enqueue_task(
    task_id,
    priority: int = 0,
) -> None:
    """
    Add a task ID to the Redis queue.

    Only the integer task ID is stored in Redis.
    """

    normalized_id = normalize_task_id(task_id)

    await redis_client.rpush(
        TASK_QUEUE,
        str(normalized_id),
    )


async def dequeue_task() -> str | None:
    """
    Remove and return one task ID from Redis.

    Returns None when the queue is empty after the timeout.
    """

    result = await redis_client.blpop(
        TASK_QUEUE,
        timeout=5,
    )

    if result is None:
        return None

    _, task_id = result

    return task_id


async def get_queue_length() -> int:
    """
    Return the current number of queued tasks.
    """

    return await redis_client.llen(TASK_QUEUE)


async def clear_task_queue() -> int:
    """
    Delete the AgentMesh task queue.

    Returns the number of items that existed before deletion.
    """

    queue_length = await redis_client.llen(TASK_QUEUE)

    await redis_client.delete(TASK_QUEUE)

    return int(queue_length)