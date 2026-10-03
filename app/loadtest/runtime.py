from __future__ import annotations

import asyncio
import time
from typing import Any


class LoadTestRuntime:

    def __init__(
        self,
        execution_delay_ms: int = 20,
    ):

        self.execution_delay_ms = (
            execution_delay_ms
        )

    async def execute(
        self,
        agent: Any,
        task: Any,
    ) -> dict:

        start = time.perf_counter()

        await asyncio.sleep(
            self.execution_delay_ms / 1000
        )

        duration = (
            time.perf_counter()
            - start
        )

        return {
            "benchmark": True,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "task_id": task.id,
            "task_type": task.task_type,
            "status": "simulated_success",
            "execution_latency_seconds": round(
                duration,
                6,
            ),
        }