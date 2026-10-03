
from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

# IMPORTANT:
# Register all SQLAlchemy models before ORM queries are executed.
from app.db import models

from app.core.redis import redis_client
from app.db.database import SessionLocal
from app.loadtest.loadtest import (
    create_benchmark_tasks,
    get_test_agent,
    get_test_owner,
)
from app.models.task import Task
from app.queue.task_queue import enqueue_task


RESULTS_DIR = Path("artifacts") / "load_tests"
QUEUE_NAME = "agentmesh:tasks"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AgentMesh distributed load benchmark."
    )

    parser.add_argument(
        "--tasks",
        type=int,
        default=100,
        help="Number of benchmark tasks to create.",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of workers expected to process the benchmark.",
    )

    parser.add_argument(
        "--delay-ms",
        type=int,
        default=20,
        help="Simulated execution delay in milliseconds.",
    )

    return parser.parse_args()


def normalize_task_ids(tasks_or_ids) -> list[int]:
    """
    Convert either Task ORM objects or integer task IDs into
    a clean list of integer task IDs.
    """

    task_ids: list[int] = []

    for item in tasks_or_ids:
        if isinstance(item, Task):
            if item.id is None:
                raise ValueError("Encountered a Task without an ID.")
            task_ids.append(int(item.id))
        else:
            task_ids.append(int(item))

    return task_ids


async def wait_for_completion(
    db: Session,
    task_ids,
    timeout_seconds: int = 300,
) -> dict:
    """
    Wait until all benchmark tasks reach a terminal state.

    Returns counts for completed, failed, queued and running tasks.
    """

    task_ids = normalize_task_ids(task_ids)

    if not task_ids:
        return {
            "completed": 0,
            "failed": 0,
            "queued": 0,
            "running": 0,
            "timed_out": False,
        }

    start_time = time.monotonic()

    while True:
        elapsed = time.monotonic() - start_time

        rows = db.execute(
            select(
                Task.status,
                func.count(Task.id),
            )
            .where(Task.id.in_(task_ids))
            .group_by(Task.status)
        ).all()

        status_counts = {
            str(status): int(count)
            for status, count in rows
        }

        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        queued = status_counts.get("queued", 0)
        running = status_counts.get("running", 0)

        terminal_count = completed + failed

        if terminal_count >= len(task_ids):
            return {
                "completed": completed,
                "failed": failed,
                "queued": queued,
                "running": running,
                "timed_out": False,
            }

        if elapsed >= timeout_seconds:
            return {
                "completed": completed,
                "failed": failed,
                "queued": queued,
                "running": running,
                "timed_out": True,
            }

        await asyncio.sleep(1)

        # Refresh the SQLAlchemy session so the next query sees
        # the worker's latest PostgreSQL updates.
        db.expire_all()


async def enqueue_all(task_ids) -> int:
    """
    Push all task IDs into Redis.
    """

    task_ids = normalize_task_ids(task_ids)

    for task_id in task_ids:
        await enqueue_task(
            task_id=task_id,
            priority=5,
        )

    return len(task_ids)


def get_task_latencies(
    db: Session,
    task_ids,
) -> list[float]:
    """
    Return task execution latency in seconds.

    Latency is measured from started_at to completed_at.
    """

    task_ids = normalize_task_ids(task_ids)

    if not task_ids:
        return []

    tasks = db.execute(
        select(Task)
        .where(Task.id.in_(task_ids))
        .order_by(Task.id.asc())
    ).scalars().all()

    latencies: list[float] = []

    for task in tasks:
        if task.started_at is None:
            continue

        if task.completed_at is None:
            continue

        latency = (
            task.completed_at - task.started_at
        ).total_seconds()

        if latency >= 0:
            latencies.append(latency)

    return latencies


def get_total_duration(
    db: Session,
    task_ids,
) -> float:
    """
    Calculate total benchmark duration using the earliest start time
    and latest completion time.
    """

    task_ids = normalize_task_ids(task_ids)

    if not task_ids:
        return 0.0

    tasks = db.execute(
        select(Task)
        .where(Task.id.in_(task_ids))
    ).scalars().all()

    started_times = [
        task.started_at
        for task in tasks
        if task.started_at is not None
    ]

    completed_times = [
        task.completed_at
        for task in tasks
        if task.completed_at is not None
    ]

    if not started_times or not completed_times:
        return 0.0

    earliest_start = min(started_times)
    latest_completion = max(completed_times)

    duration = (
        latest_completion - earliest_start
    ).total_seconds()

    return max(duration, 0.0)


def build_report(
    *,
    task_count: int,
    worker_count: int,
    delay_ms: int,
    completion: dict,
    latencies: list[float],
    duration_seconds: float,
    enqueue_seconds: float,
) -> dict:
    """
    Build the JSON benchmark report.
    """

    completed = completion["completed"]
    failed = completion["failed"]

    total_terminal = completed + failed

    success_rate = (
        completed / task_count
        if task_count > 0
        else 0.0
    )

    failure_rate = (
        failed / task_count
        if task_count > 0
        else 0.0
    )

    if duration_seconds > 0:
        throughput = completed / duration_seconds
    else:
        throughput = 0.0

    if latencies:
        average_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
    else:
        average_latency = 0.0
        median_latency = 0.0
        min_latency = 0.0
        max_latency = 0.0

    return {
        "benchmark": "AgentMesh Distributed Load Test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tasks": task_count,
        "workers": worker_count,
        "execution_delay_ms": delay_ms,
        "completed": completed,
        "failed": failed,
        "queued": completion["queued"],
        "running": completion["running"],
        "terminal_tasks": total_terminal,
        "success_rate": round(success_rate, 4),
        "failure_rate": round(failure_rate, 4),
        "throughput_tasks_per_second": round(throughput, 4),
        "enqueue_seconds": round(enqueue_seconds, 4),
        "duration_seconds": round(duration_seconds, 4),
        "latency": {
            "sample_count": len(latencies),
            "average_seconds": round(average_latency, 4),
            "median_seconds": round(median_latency, 4),
            "min_seconds": round(min_latency, 4),
            "max_seconds": round(max_latency, 4),
        },
        "timed_out": completion["timed_out"],
    }


def save_report(
    report: dict,
    task_count: int,
    worker_count: int,
) -> Path:
    """
    Save benchmark results to artifacts/load_tests.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"benchmark_"
        f"{task_count}_tasks_"
        f"{worker_count}_workers.json"
    )

    output_path = RESULTS_DIR / filename

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    return output_path


async def run_benchmark(
    task_count: int,
    worker_count: int,
    delay_ms: int,
) -> dict:
    """
    Execute one complete AgentMesh load benchmark.
    """

    print()
    print("=" * 70)
    print("AgentMesh Distributed Load Test")
    print("=" * 70)
    print(f"Tasks       : {task_count}")
    print(f"Workers     : {worker_count}")
    print(f"Delay       : {delay_ms} ms")
    print("=" * 70)

    db = SessionLocal()

    try:
        # ------------------------------------------------------------
        # 1. Find benchmark owner
        # ------------------------------------------------------------
        owner = get_test_owner(
            db=db,
        )

        # ------------------------------------------------------------
        # 2. Find or create benchmark agent
        # ------------------------------------------------------------
        agent = get_test_agent(
            db=db,
            owner_id=owner.id,
        )

        # ------------------------------------------------------------
        # 3. Create benchmark tasks in PostgreSQL
        # ------------------------------------------------------------
        tasks = create_benchmark_tasks(
            db=db,
            owner_id=owner.id,
            agent_id=agent.id,
            count=task_count,
        )

        # IMPORTANT:
        # Convert ORM objects into integer IDs immediately.
        task_ids = normalize_task_ids(tasks)

        print(f"Created {len(task_ids)} tasks.")

        # ------------------------------------------------------------
        # 4. Check Redis queue before benchmark
        # ------------------------------------------------------------
        queue_before = await redis_client.llen(
            QUEUE_NAME,
        )

        print(f"Queue before: {queue_before}")

        # ------------------------------------------------------------
        # 5. Enqueue tasks
        # ------------------------------------------------------------
        enqueue_start = time.perf_counter()

        await enqueue_all(
            task_ids,
        )

        enqueue_seconds = (
            time.perf_counter() - enqueue_start
        )

        print(
            f"Enqueued {len(task_ids)} tasks "
            f"in {enqueue_seconds:.4f}s"
        )

        # ------------------------------------------------------------
        # 6. Wait for workers
        # ------------------------------------------------------------
        result = await wait_for_completion(
            db=db,
            task_ids=task_ids,
            timeout_seconds=300,
        )

        # ------------------------------------------------------------
        # 7. Read latency information
        # ------------------------------------------------------------
        latencies = get_task_latencies(
            db=db,
            task_ids=task_ids,
        )

        # ------------------------------------------------------------
        # 8. Calculate benchmark duration
        # ------------------------------------------------------------
        duration_seconds = get_total_duration(
            db=db,
            task_ids=task_ids,
        )

        # If timestamps aren't available, fall back to zero.
        if duration_seconds <= 0:
            duration_seconds = 0.0

        # ------------------------------------------------------------
        # 9. Build report
        # ------------------------------------------------------------
        report = build_report(
            task_count=task_count,
            worker_count=worker_count,
            delay_ms=delay_ms,
            completion=result,
            latencies=latencies,
            duration_seconds=duration_seconds,
            enqueue_seconds=enqueue_seconds,
        )

        # ------------------------------------------------------------
        # 10. Save report
        # ------------------------------------------------------------
        output_path = save_report(
            report=report,
            task_count=task_count,
            worker_count=worker_count,
        )

        # ------------------------------------------------------------
        # 11. Print summary
        # ------------------------------------------------------------
        print()
        print("=" * 70)
        print("Benchmark Complete")
        print("=" * 70)
        print(
            f"Completed   : {report['completed']}"
        )
        print(
            f"Failed      : {report['failed']}"
        )
        print(
            f"Queued      : {report['queued']}"
        )
        print(
            f"Running     : {report['running']}"
        )
        print(
            f"Success     : {report['success_rate'] * 100:.2f}%"
        )
        print(
            f"Throughput  : "
            f"{report['throughput_tasks_per_second']:.4f} tasks/s"
        )
        print(
            f"Avg latency : "
            f"{report['latency']['average_seconds']:.4f}s"
        )
        print(
            f"Duration    : "
            f"{report['duration_seconds']:.4f}s"
        )
        print(
            f"Timed out   : {report['timed_out']}"
        )
        print(
            f"Report      : {output_path}"
        )
        print("=" * 70)

        return report

    finally:
        db.close()


async def main() -> None:
    args = parse_arguments()

    if args.tasks <= 0:
        raise ValueError(
            "--tasks must be greater than zero."
        )

    if args.workers <= 0:
        raise ValueError(
            "--workers must be greater than zero."
        )

    if args.delay_ms < 0:
        raise ValueError(
            "--delay-ms cannot be negative."
        )

    await run_benchmark(
        task_count=args.tasks,
        worker_count=args.workers,
        delay_ms=args.delay_ms,
    )


if __name__ == "__main__":
    asyncio.run(main())
