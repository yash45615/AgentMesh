import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=None,
)


TASK_QUEUE = "agentmesh:tasks"


async def enqueue_task(task_id: str) -> None:
    await redis_client.rpush(
        TASK_QUEUE,
        task_id,
    )


async def dequeue_task() -> str | None:
    result = await redis_client.blpop(
        TASK_QUEUE,
        timeout=5,
    )

    if result is None:
        return None

    _, task_id = result

    return task_id