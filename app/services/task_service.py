from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.task import Task
from app.schemas.task import TaskCreate


def create_task(
    db: Session,
    owner_id: int,
    data: TaskCreate,
) -> Task:

    agent = db.execute(
        select(Agent).where(
            Agent.id == data.agent_id,
            Agent.owner_id == owner_id,
            Agent.is_active.is_(True),
        )
    ).scalar_one_or_none()

    if agent is None:
        raise ValueError("Agent not found or inactive")

    task = Task(
        owner_id=owner_id,
        agent_id=data.agent_id,
        task_type=data.task_type,
        input_data=data.input_data,
        priority=data.priority,
        max_retries=data.max_retries,
        timeout_seconds=data.timeout_seconds,
        status="queued",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(
    db: Session,
    task_id: int,
    owner_id: int,
) -> Task | None:

    statement = select(Task).where(
        Task.id == task_id,
        Task.owner_id == owner_id,
    )

    return db.execute(statement).scalar_one_or_none()


def get_tasks(
    db: Session,
    owner_id: int,
) -> list[Task]:

    statement = (
        select(Task)
        .where(Task.owner_id == owner_id)
        .order_by(
            Task.priority.desc(),
            Task.created_at.asc(),
        )
    )

    return list(
        db.execute(statement)
        .scalars()
        .all()
    )


def mark_task_running(
    db: Session,
    task: Task,
) -> Task:

    task.status = "running"
    task.started_at = datetime.utcnow()
    task.error_message = None

    db.commit()
    db.refresh(task)

    return task


def mark_task_completed(
    db: Session,
    task: Task,
    result: dict,
) -> Task:

    task.status = "completed"
    task.result = result
    task.completed_at = datetime.utcnow()
    task.error_message = None

    db.commit()
    db.refresh(task)

    return task


def mark_task_failed(
    db: Session,
    task: Task,
    error_message: str,
) -> Task:

    task.status = "failed"
    task.error_message = error_message
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def retry_task(
    db: Session,
    task: Task,
) -> Task:

    task.retry_count += 1
    task.status = "queued"
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    task.worker_id = None

    db.commit()
    db.refresh(task)

    return task