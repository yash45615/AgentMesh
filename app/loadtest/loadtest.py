from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models

from app.models.user import User
from app.models.agent import Agent
from app.models.task import Task


def get_test_owner(db: Session) -> User:
    """
    Return an existing AgentMesh user to own benchmark tasks.

    The load test uses a real database user so that benchmark tasks
    follow the same ownership model as normal AgentMesh tasks.
    """

    owner = db.execute(
        select(User).order_by(User.id.asc())
    ).scalars().first()

    if owner is None:
        raise RuntimeError(
            "No AgentMesh user exists. Create a user before running the load test."
        )

    return owner


def get_test_agent(db: Session, owner_id: int) -> Agent:
    """
    Return an existing agent belonging to the supplied owner.

    If no agent exists, create a dedicated benchmark agent.
    """

    agent = db.execute(
        select(Agent)
        .where(Agent.owner_id == owner_id)
        .order_by(Agent.id.asc())
    ).scalars().first()

    if agent is not None:
        return agent

    agent = Agent(
        owner_id=owner_id,
        name="AgentMesh Benchmark Agent",
        description="Dedicated agent used for distributed load testing.",
        agent_type="benchmark",
        model="benchmark-runtime",
        system_prompt="Execute benchmark tasks deterministically.",
        capabilities={
            "benchmark": True,
            "load_testing": True,
        },
        allowed_tools=[],
        configuration={
            "benchmark": True,
        },
        max_concurrent_tasks=10,
        timeout_seconds=300,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


def create_benchmark_tasks(
    db: Session,
    owner_id: int,
    agent_id: int,
    count: int,
) -> list[Task]:
    """
    Create benchmark tasks in PostgreSQL.

    Tasks are initially placed in QUEUED state. The benchmark runner
    subsequently pushes their IDs into Redis for workers to consume.
    """

    if count <= 0:
        raise ValueError("Benchmark task count must be greater than zero.")

    tasks: list[Task] = []

    for index in range(1, count + 1):
        task = Task(
            owner_id=owner_id,
            agent_id=agent_id,
            task_type="benchmark",
            input_data={
                "benchmark": True,
                "sequence": index,
                "created_for": "agentmesh-load-test",
            },
            result=None,
            error_message=None,
            status="queued",
            priority=5,
            retry_count=0,
            max_retries=3,
            timeout_seconds=300,
        )

        db.add(task)
        tasks.append(task)

    db.commit()

    for task in tasks:
        db.refresh(task)

    return tasks


def cleanup_old_benchmark_tasks(
    db: Session,
    older_than_minutes: int = 60,
) -> int:
    """
    Optional helper that removes old benchmark tasks.

    This is not required for normal benchmark execution, but can be
    useful when repeatedly running load tests against a development DB.
    """

    if older_than_minutes <= 0:
        raise ValueError("older_than_minutes must be greater than zero.")

    cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)

    old_tasks = db.execute(
        select(Task).where(
            Task.task_type == "benchmark",
            Task.created_at < cutoff,
        )
    ).scalars().all()

    count = len(old_tasks)

    for task in old_tasks:
        db.delete(task)

    if count:
        db.commit()

    return count